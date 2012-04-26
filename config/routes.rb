DatascienceScSite::Application.routes.draw do

  get  'tech' => 'home#tech', :as => :tech

  get  'predict' => 'home#predict', :as => :predict
  post 'predict' => 'home#predict_post'

  root :to => 'home#index', :as => :home

end
