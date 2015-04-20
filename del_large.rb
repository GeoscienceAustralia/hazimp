#!/usr/bin/env ruby
 
module ShrinkIt
  BUCKETS = 4
 
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

# GitHub has a max file limit of 100M.
# patong.sts and flood.tif exceed this limit
large_files << "validation_tests/case_studies/patong/boundaries/mux_small/patong.sts"
large_files << "demos/cairns/*"

large_files << "demos/checkpointing/merimbula_17156.tsh" 
large_files << "source/anuga_parallel/pymetis/metis-4.0/Doc/*"
large_files << "source/anuga_parallel/merimbula_17156.tsh"
large_files << "source/anuga_parallel/merimbula_43200.tsh"
large_files << "source/anuga_parallel/merimbula_43200_1.tsh"
large_files << "source/anuga_parallel/data/*"
large_files << "source/anuga_parallel/examples/*"
large_files << "source/anuga/lib/maxasc/perthAll_stage_250m.asc"
large_files << "source/anuga/lib/maxasc/perthAll_stage_250m_all.asc"
large_files << "source/anuga/lib/maxasc/perthAll_stage_250m_original.asc"
large_files << "source/anuga/lib/maxasc/perthAll_stage_original.asc"
large_files << "source/anuga/alpha_shape/wiki/*"
large_files << "source/anuga/extras/*"
large_files << "source/anuga/shallow_water_balanced/domain.sww"
large_files << "source/anuga/abstract_2d_finite_volumes/hires2.zip"
large_files << "source/anuga/examples/beach.tsh"
large_files << "source/anuga/pyvolution/hires2.zip"
large_files << "source/anuga_viewer/*"
large_files << "source/contributed_code/*"
large_files << "source/anuga_validation_tests/*"
large_files << "source/swollen_viewer/*"
large_files << "swollen_viewer/*"
large_files << "install/*"
large_files << "source_numpy_conversion/*"
large_files << "validation_tests/case_studies/towradgi/DEM_bridges/*"
large_files << "validation_tests/case_studies/towradgi/DEM/*"
large_files << "validation_tests/case_studies/patong/topographies/*"
large_files << "validation_tests/case_studies/patong/meshes/*"
large_files << "validation_tests/case_studies/patong/polygons/*"
large_files << "validation_tests/case_studies/merewether/*.asc"
large_files << "validation_tests/case_studies/okushiri/*"
large_files << "validation_tests/Tests/Experimental/Okushiri/Benchmark_2.msh"
large_files << "validation_tests/Tests/Analytical/Dam_Break/dam_break.sww"
large_files << "validation_tests/Tests/Case_studies/*"
large_files << "validation_tests/Tests/Benchmarks/Okushiri/Benchmark_2_Bathymetry.txt"
large_files << "validation_tests/Tests/Benchmarks/Okushiri/Benchmark_2_Bathymetry.pts"
large_files << "validation_tests/Tests/Other_References/radial_dam_break_wet/Ver_numerical_2.000000.csv"
large_files << "validation_tests/Tests/Benchmarks/Okushiri/Benchmark_2.msh"
large_files << "validation_tests/Tests/Experimental/Okushiri/Benchmark_2_Bathymetry.pts"
large_files << "validation_tests/experimental_data/okushiri/Benchmark_2_Bathymetry.txt"
large_files << "documentation/*"  
large_files << "user_manual/anuga_user_manual.pdf"
large_files << "source/anuga_parallel/documentation/*"  

# Big files to keep

# large_files << "validation_tests/case_studies/*"    # exists
# large_files << "validation_tests/experimental_data/okushiri/*"     # exists
# doc/anuga_user_manual.pdf    # exists
# validation_tests/experimental_data/okushiri/Benchmark_2_Bathymetry.pts    # exists
# examples/cairns/cairns.zip    # exists

ShrinkIt.remove(large_files)
