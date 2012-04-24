#!/usr/bin/env ruby

require './match_scraper'
require 'optparse'

def main

  options = {
    :delay => 5
  }

  OptionParser.new do |opts|
    opts.banner = "Usage: #{$0} [options] [section=sc2-international]"

    opts.on('-p', '--start-page N', Integer, 'Start at page N (inclusive)') {|n| options[:start_page] = n}
    opts.on('-q', '--end-page N', Integer, 'End at page N (inclusive)') {|n| options[:end_page] = n}
    opts.on('-d', '--delay D', Float, 'Inter-request delay (seconds)') {|d| options[:delay] = d}
    opts.on('-f', '--file HTML', 'Scrape file HTML instead of the web') {|path| options[:file] = path}
    opts.on('-b', '--browse', 'Open browser instead of scraping') { options[:browse] = true }

    # TODO (jonko)
    opts.on('-l', '--log LOGFILE', 'Set log file') {|path| raise NotImplementedError}
    opts.on('-o', '--output RESULTS', 'Set results CSV') {|path| raise NotImplementedError}

    opts.on_tail('-h', '--help', 'Display this message') { puts opts; exit }
  end.parse!

  options[:section] = ARGV.first if ARGV.any?
  s = MatchScraper.new(options)
  s.scrape!

end

main
