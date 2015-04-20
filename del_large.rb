#!/usr/bin/env ruby
 
module ShrinkIt
  BUCKETS = 1
 
  def self.remove(files)
    files.each_slice(files.size / BUCKETS) do |portion|
      paths = portion.join(" ")
      ShrinkIt.stream_command("git filter-branch -f --index-filter 'git rm --cached --ignore-unmatch #{paths}' -- --all")
      ShrinkIt.stream_command("rm -rf .git/refs/original/")
      ShrinkIt.stream_command("git reflog expire --expire=now --all")
      ShrinkIt.stream_command("git fsck --full --unreachable")
      ShrinkIt.stream_command("git repack -A -d")
      ShrinkIt.stream_command("git gc --aggressive --prune=now")
    end
  end
 
  def self.stream_command(cmd)
    puts "#{Time.new} Starting #{cmd}"
    IO.popen(cmd) do |data|
      while line = data.gets
        puts line
      end
    end
  end
end
 
large_files = []

large_files << "hazimp_preprocessing/Documentation/hazimp.EAP" 
large_files << "examples/anuga_flood/big_sydney.asc" 


large_files << "examples/anuga_flood/*" 
large_files << "examples/flood/results.csv" 
large_files << "examples/wind/wind_impact.csv"

# Let's have all the curves in there
#large_files << "hazimp_preprocessing/curve_data/content_flood_vul_curves.xml" 
#large_files << "hazimp_preprocessing/curve_data/contents_synthetic.xml"
#large_files << "hazimp_preprocessing/curve_data/fabric_flood_vul_curves.xml" 
#large_files << "hazimp_preprocessing/curve_data/fabric_synthetic.xml"
#large_files << "hazimp_preprocessing/curve_data/structural_synthetic.xml" 
#large_files << "hazimp_preprocessing/curve_data/synthetic_domestic_wind_vul_curves.xml"

ShrinkIt.remove(large_files)
