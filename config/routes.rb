DatascienceScSite::Application.routes.draw do

  get  'tech' => 'home#tech', :as => :tech

  root :to => 'home#index', :as => :home

end
