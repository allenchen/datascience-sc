require 'logger'

class MultiIO
# http://stackoverflow.com/questions/6407141/how-can-i-have-ruby-logger-log-output-to-stdout-as-well-as-file

  def initialize(*targets)
     @targets = targets
  end

  def write(*args)
    @targets.each {|t| t.write(*args); t.flush}
  end

  def close
    @targets.each(&:close)
  end
end

LogFile = File.open(File.join('log', "log_#{Time.now.to_i}.log"), "a")
Log = Logger.new(MultiIO.new(STDOUT, LogFile))

