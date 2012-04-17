#!/usr/bin/env ruby

require './scraper'
require 'optparse'

def main

  options = {
    :delay => 5
  }

  OptionParser.new do |opts|
    opts.banner = "Usage: #{$0} [options] [section=sc2-international]"

    opts.on('-p', '--page N', 'Start at page N') {|n| options[:page] = n}
    opts.on('-d', '--delay D', 'Inter-request delay (seconds)') {|d| options[:delay] = d}
    opts.on('-f', '--file HTML', 'Scrape file HTML instead of the web') {|path| options[:file] = path}

    # TODO (jonko)
    opts.on('-l', '--log LOGFILE', 'Set log file') {|path| raise NotImplementedError}
    opts.on('-o', '--output RESULTS', 'Set results CSV') {|path| raise NotImplementedError}

    opts.on_tail('-h', '--help', 'Display this message') { puts opts; exit }
  end.parse!

  options[:section] = ARGV.first if ARGV.any?
  s = Scraper.new(options)
  s.scrape!

end

main
