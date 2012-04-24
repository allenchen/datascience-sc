require './scraper'

class MapScraper < Scraper

  Header = [ :id, :name,
             :size, :spots
           ]

  BasePageUrl = 'http://www.teamliquid.net/tlpd/sc2-international/maps/'
  Folder = File.join('results', 'maps')

  def parse_row(tr)
    result = {}

    map_link = tr.css('td')[1].at('a')
    result[:id] = File.basename(map_link['href']).to_i
    @mech.transact do
      @mech.click map_link
      Log.info "Scraping #{@mech.page.title}"
      p = @mech.page.search('.roundcont p')[1]
      text = p.search('text()').collect(&:text).collect(&:strip)
      text = text[3..-1]
      text.drop_while {|s| s.empty?}

      result[:name]  = text[0]

      if result[:name] =~ /Unknown/
        result[:name] = 'Unknown'
        result[:size], result[:spots] = nil, nil
      else
        text = text.slice_before {|s| s =~ /Size/}.to_a.last
        result[:size] = text[1].scan(/(\d+x\d+)/).flatten.first

        text = text.slice_before {|s| s =~ /Spots/}.to_a.last
        result[:spots] = text[1].scan(/(\d+)/).flatten.join(',')
      end

      Log.debug result.inspect
    end

    result
  end

end
