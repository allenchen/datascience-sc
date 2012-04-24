#!/usr/bin/env ruby

require 'mechanize'
require 'open-uri'
require 'addressable/uri'
require 'csv'
require './util'

module Scrapeable
  # Paths
  Folder   = proc {|s| File.join('results', s.options[:section]) }
  Filename = "results_#{Time.now.to_i}.csv"

  # Header fields
  Header = proc { raise NotImplementedError }

  # Configuration variables
  UserAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19'

  # Page URL without query params
  BasePageUrl = proc { raise NotImplementedError } # 'http://www.teamliquid.net/tlpd/games/index.php'

  # Default query params, if any
  DefaultPageUrlOpts = proc { {} }

  # Pluggable hooks, run before or after some action
  # Should all be +lambda+s.

  # Run after scraping all pages
  PostScrape = nil
end

class Scraper

  attr_accessor :page, :results, :options

  include Scrapeable

  # @param [Hash] options
  # @param options [String]  :section    default "sc2-international"
  # @param options [Integer] :start_page Start page, default 1
  # @param options [Integer] :end_page   End page, default nil
  # @param options [Float]   :delay      Inter-request delay (throttling)
  # @param options [String]  :file       Scrape this file instead of web
  # @param options [Boolean] :browse     Open browser instead of scraping
  #
  def initialize(options={}) #section="sc2-international")
    @options = {
      :section    => "sc2-international",
      :start_page => nil,
      :end_page   => nil,
      :delay      => 5,
      :browse     => false
    }.merge(options)

    @page = nil

    # Maps from ID to object
    @maps = {}
    @leagues = {}
    @players = {}

    @results = []
    @mech = Mechanize.new do |agent|
      agent.user_agent = get_config_value(self.class::UserAgent)
    end
  end

  def scrape!
    page_num = @options[:start_page]
    Log.info "Starting on page #{page_num}" if page_num

    if @options[:browse]
      url = page_url(:page => page_num)
      puts url
      `google-chrome "#{url}"`
      return
    end

    dump_header
    while next_page!(page_num)
      page_num = nil
      dump_results
      sleep @options[:delay]
    end
  end

  private

  # Creates log folder and returns path (@see {Paths::Filename}, {Paths::Folder})
  def results_log_path
    results_log_name = get_config_value(self.class::Filename)
    results_folder   = get_config_value(self.class::Folder)
    FileUtils.mkdir_p(results_folder)
    File.join(results_folder, results_log_name)
  end

  # @param result [Hash]
  def format_result(result)
    get_config_value(self.class::Header).collect do |field|
      result[field]
    end
  end

  def dump_header
    path = File.join(File.dirname(results_log_path), 'header.csv')
    CSV.open(path, 'wt') do |csv|
      csv << get_config_value(self.class::Header)
    end
  end

  def dump_results
    Log.debug "Taking a dump..."

    CSV.open(results_log_path, 'at') do |csv|
      @results.each do |result|
        csv << format_result(result)
      end
    end
    @results.clear
  end

  def next_page!(start_page=nil)
    begin

      # source = file
      if @options[:file] and File.readable?(@options[:file])
        Log.info "Using file #{@options[:file]}"
        File.open(@options[:file]) { |f| @page = Nokogiri::HTML(f) }

      else # source = web
        if @page and start_page.nil?
          unless next_link = @mech.page.link_with(:text => '>')
            return false
          end
          @page = next_link.click
        else
          url = page_url(:page => start_page)
          Log.debug "Starting at url #{url}"
          @mech.get(url)
          @page = @mech.page
        end
      end

      page_number = @page.search('input[name=tabulator_page]').first['value'].to_i
      if @options[:end_page] and page_number > @options[:end_page].to_i
        Log.info "Requested to stop at page #{@options[:end_page]}, so stopping."
        return
      else
        Log.info "Scraping page #{page_number}"
      end

      rows = @page.search('#tblt_table tr')[1..-1]  # exclude header
      rows.each do |row|
        @results << parse_row(row)
      end
    rescue OpenURI::HTTPError, Mechanize::ResponseCodeError => e
      if e.message.to_i == 503
        #@options[:delay] *= 2
        Log.debug "Timed out, delay = #{@options[:delay]}"
        sleep @options[:delay]
        retry
      else
        raise
      end
    end

    if hook = self.class::PostScrape
      get_config_value(self.class::PostScrape)
    end

    return true
  end

  # Converts a +tr+ to a +Hash+ for collection into {results}.
  # Exact format of the return value is unspecified, but will should be
  # understandable by {format_result}.
  #
  # @param tr [Nokogiri::Node] scraped table row
  # @return [Hash] representing this row
  #
  def parse_row(tr)
    raise NotImplementedError, "Scraper::parse_row"
  end

  def page_url(opts={})
    base_url = get_config_value(self.class::BasePageUrl)

    opts = {
      :page => 1
    }.merge(get_config_value(self.class::DefaultPageUrlOpts)).merge(opts)

    query = {
      'tabulator_page'       => opts.delete(:page),
      'tabulator_order_col'  => 1,
      'tabulator_order_desc' => 1,
#      'tabulator_search'     => "#tblt-3922-#{opts[:page]}-1-DESC"
    }.merge(opts.convert_keys)

    uri = Addressable::URI.parse(base_url)
    uri.query_values = query

    uri = uri.to_s.gsub('%23', '#')  # wtf

    return uri
  end

  # Gets a configuration value. If +obj+ is a +Proc+, it's called with +self+,
  # else the value is just +obj+ itself.
  # @param obj [Object] something to get the value of
  # @return [Object]
  def get_config_value(obj)
    case obj
    when Proc
      obj.call(self)
    else
      obj
    end
  end

end

def main
  s = Scraper.new(:section => "sc2-international")
  s.scrape!
end

main if __FILE__ == $0
