# CS194-16 Data Science Final Project -- Something to do with Starcraft 2

Allen Chen, Jonathan Ko, Young Kim

## Data Collection

We obtain our dataset by scraping the game results listings from [teamliquid](http://www.teamliquid.net/tlpd/sc2-international/games). A script is provided in `scraper/main.rb` that parses the listings pages and outputs to `csv`.

Data collection is very time-consuming due to the fact that the teamliquid site throttles requests; too many requests in a short time will result in a temporary (~1 minute) IP ban. To fix this we introduce an inter-request delay of 10 seconds.
