"""
Aggregating impact data into a chloropleth map.
"""

import pandas
import geopandas

def chloropleth(impactfile, shapefile, outputfile):

    left, right = mergefield = 'MESHBLOCK_CODE_2011', 'MB_CODE11'

    impact = pandas.read_csv(impactfile)

    report = {'REPLACEMENT_VALUE': 'sum', 
              'structural_loss_ratio': 'mean', 
              '0.2s gust at 10m height m/s': 'max'}

    aggregate = impact.groupby(left).agg(report)    

    shapes = geopandas.read_file(shapefile)

    shapes['key'] = shapes[right].astype(int)

    result = shapes.merge(aggregate, left_on='key', right_index=True)

    result.to_file(outputfile)

#if __name__ == '__main__':
#    chloropleth('../example/wind_impact.csv', 
#                'examples/wind/northwestcape_meshblocks.geojson',
#                'chloropleth.shp')
