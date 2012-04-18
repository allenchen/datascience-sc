#!/usr/bin/env ruby

require 'mechanize'
require 'open-uri'
require 'addressable/uri'
require 'csv'
require './util'

class Scraper

  attr_accessor :page, :results

  Header = [ :date,
             :league_id, :league_name,
             :map_id, :map_name,
             :winner_id, :winner_name, :winner_race,
             :loser_id, :loser_name, :loser_race
           ]
  module Formats
    Date = '%Y-%m-%d'
  end

  # @param [Hash] options
  # @param options [String] :section default "sc2-international"
  # @param options [Integer] :page Start page, default 1
  # @param options [Float] :delay Inter-request delay (throttling)
  # @param options [String] :file Scrape this file instead of web
  def initialize(options={}) #section="sc2-international")
    @options = {
      :section => "sc2-international",
      :page    => nil,
      :delay   => 5
    }.merge(options)

    @page = nil
    @results_log_name = "results_#{Time.now.to_i}.csv"

    @results_folder = File.join('results', @options[:section])
    FileUtils.mkdir_p(@results_folder)

    # Maps from ID to object
    @maps = {}
    @leagues = {}
    @players = {}

    @results = []
    @mech = Mechanize.new do |agent|
      agent.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19'
    end
  end

  def scrape!
    page_num = @options[:page]
    Log.info "Starting on page #{page_num}" if page_num

    dump_header
    while next_page!(page_num)
      page_num = nil
      dump_results
      sleep @options[:delay]
    end
  end

  private

  # @param result [Hash]
  def format_result(result)
    Header.collect do |field|
      result[field]
    end
  end

  def dump_header
    path = File.join(@results_folder, 'header.csv')
    CSV.open(path, 'wt') do |csv|
      csv << Header
    end
  end

  def dump_results
    Log.debug "Taking a dump..."
    path = File.join(@results_folder, @results_log_name)

    CSV.open(path, 'at') do |csv|
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
      Log.info "Scraping page #{page_number}"

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

    begin # logging
      dates = @results.collect {|r| r[:date]}
      Log.debug "Parsed dates from #{dates.min} to #{dates.max}"
    end

    return true
  end

  def parse_row(tr)
    result = {}

    date, league, map, winner, loser = tr.css('td')[1..5]

    result[:date] = begin
      yy, mm, dd = date.text().split('-').collect(&:to_i) #.collect {|x| x<=0 ? 1 : x}
      yy += 2000

      Log.warn "Zero in date: #{[yy,mm,dd].join('-')}. Changing to 1." if mm <= 0 or dd <= 0
      mm = 1 if mm <= 0
      dd = 1 if dd <= 0

      date = Time.new(yy, mm, dd).strftime(Formats::Date)
    end

    { :winner_race => winner, :loser_race => loser }.each_pair do |label, td|
      result[label] = begin
        img = td.at_css('img')
        if img
          img['title']
        else
          log.warn "Unknown race for #{label}"
          'UNKNOWN'
        end
      end
    end

    league, map, winner, loser = [league, map, winner, loser].collect do |td|
      id_name = if a = td.at_css('a')
        a['href']
      else
        '0_UNKNOWN'
      end
      File.basename(id_name)
    end

    league, map, winner, loser = [
      [ league, :league ],
      [ map, :map ],
      [ winner, :winner ],
      [ loser, :loser ]
    ].collect do |text, label|
      id, name = text.scan(/(\d+)_(.*)/).flatten.collect {|s| URI.unescape(s)}
      result[ "#{label}_id".to_sym ]   = id
      result[ "#{label}_name".to_sym ] = name
    end

    result
  end

  def page_url(opts={})
    #return "http://www.teamliquid.net/tlpd/sc2-international/games"

    base_url = "http://www.teamliquid.net/tlpd/games/index.php"

    opts = {
      :page => 1
    }.merge(opts)

    query = {
      'section'              => @options[:section],
      'tabulator_page'       => opts[:page],
      'tabulator_order_col'  => 1,
      'tabulator_order_desc' => 1,
#      'tabulator_search'     => "#tblt-3922-#{opts[:page]}-1-DESC"
    }

    uri = Addressable::URI.parse(base_url)
    uri.query_values = query

    uri = uri.to_s.gsub('%23', '#')  # wtf

    return uri
  end

end

def main
  s = Scraper.new(:section => "sc2-international")
  s.scrape!
end

main if __FILE__ == $0
