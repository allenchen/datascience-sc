#!/usr/bin/env ruby

require 'mechanize'
require 'open-uri'
require 'addressable/uri'
require 'csv'
require './util'

class Scraper

  Map    = Struct.new(:id, :name)
  League = Struct.new(:id, :name)
  Player = Struct.new(:id, :name)
  #Result = Struct.new(:date, :league, :map, :winner, :loser)

  class Result
    attr_accessor :date, :league, :map, :winner, :loser

    def initialize(date, league, map, winner, loser)
      @date, @league, @map, @winner, @loser = [date, league, map, winner, loser]
    end

    def to_a
      [@date, [@league, @map, @winner, @loser].collect {|x| [x.id, x.name]}].flatten
    end
  end

  attr_accessor :page, :results

  # @param [Hash] options
  # @param options [String] :section default "sc2-international"
  # @param options [Integer] :page Start page, default 1
  # @param options [Float] :delay Inter-request delay (throttling)
  def initialize(options={}) #section="sc2-international")
    @options = {
      :section => "sc2-international",
      :page    => nil,
      :delay   => 5
    }.merge(options)

    @page = nil

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

    while next_page!(page_num)
      page_num = nil
      dump_results
      sleep @options[:delay]
    end
  end

  private

  def dump_results
    Log.debug "Taking a dump..."
    folder = File.join('results', @options[:section])
    FileUtils.mkdir_p(folder)
    path = File.join(folder, "results_#{Time.now.to_i}.csv")

    CSV.open(path, 'at') do |csv|
      @results.each do |result|
        csv << result.to_a
      end
    end
    @results.clear
  end

  def next_page!(start_page=nil)
    begin
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

    Log.debug "Parsed dates from #{@results.collect(&:date).min} to #{@results.collect(&:date).max}"

    return true
  end

  def parse_row(tr)
    date, league, map, winner, loser = tr.css('td')[1..5]
    begin # date
      yy, mm, dd = date.text().split('-').collect(&:to_i)
      yy += 2000
      date = Time.new(yy, mm, dd)
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
      [ league, League ],
      [ map, Map ],
      [ winner, Player ],
      [ loser, Player ]
    ].collect do |text, klass|
      id, name = text.scan(/(\d+)_(.*)/).flatten.collect {|s| URI.unescape(s)}
      klass.new(id, name)
    end

    Result.new(date, league, map, winner, loser)
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
