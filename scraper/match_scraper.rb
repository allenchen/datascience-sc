require './scraper'

class MatchScraper < Scraper

  Header = [ :date,
             :league_id, :league_name,
             :map_id, :map_name,
             :winner_id, :winner_name, :winner_race,
             :loser_id, :loser_name, :loser_race
           ]
  DateFormat = '%Y-%m-%d'

  BasePageUrl = 'http://www.teamliquid.net/tlpd/games/index.php'
  DefaultPageUrlOpts = proc {|s| {'section' => s.options[:section] } }

  PostScrape = lambda do |s|
    dates = s.results.collect {|r| r[:date]}
    Log.debug "Parsed dates from #{dates.min} to #{dates.max}"
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

      date = Time.new(yy, mm, dd).strftime(DateFormat)
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
end
