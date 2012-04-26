require 'open-uri'

class HomeController < ApplicationController

  def index
  end

  def tech
  end

  def predict
  end

  def predict_post
    json = open("http://ec2-50-18-88-226.us-west-1.compute.amazonaws.com:9999/predict?date=2010-09-25&mid=383&pid=1614&prace=2&cid=2025&crace=2") {|io| io.read}
    @json = ActiveSupport::JSON.decode(json)
  end

end
