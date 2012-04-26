#!/usr/bin/env python

import model
import sys

def make_pickle(pid):
  data = model.load_data()
  model.create_model(pid, data)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Usage: this <PID>"
    exit
  make_pickle(int(sys.argv[1]))
