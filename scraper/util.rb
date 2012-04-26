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

FileUtils.mkdir_p('log')
LogFile = File.open(File.join('log', "log_#{Time.now.to_i}.log"), "a")
Log = Logger.new(MultiIO.new(STDOUT, LogFile))

class Hash
  def convert_keys(converter=:to_s)
    f = case converter
    when Symbol
      lambda {|converter, k| k.public_send(converter)}
    else
      lambda {|converter, k| converter.call(k)}
    end
    Hash[self.collect{|k,v| [f.call(converter, k), v]}]
  end

  def convert_keys!(converter=:to_s)
    self.replace(self.convert_keys(converter))
  end
end