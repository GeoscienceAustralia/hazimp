from anuga.file_conversion.sww2dem import sww2dem

# get a depth file

sww2dem('big_sydney.sww',
        'big_sydneycs800.asc',
        quantity='stage - elevation',
        cellsize=800,
        number_of_decimal_places=9,
        verbose=True,
        block_size=2)
