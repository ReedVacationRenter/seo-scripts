#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import unicodecsv as csv
import subprocess
import sys
import pandas as pd

country = sys.argv[1] #country code ie. GB
infile = sys.argv[2] #list of urls
# sitemap_type = 'totl'
 sitemap_type = 'desk'
# sitemap_type = 'mobl'
#base = "https://{0}.vacationrenter.com".format(country.lower())
base = "https://www.vacationrenter.com"
# infile = "{0}_sitemap_canons_and_mobile.tsv".format(country.upper())
sitemap_index_outfile = '{0}_sitemap_index.xml'.format(country.lower())

urldf = pd.read_csv(infile, sep='\t', header=None, encoding="utf-8")
urldf.columns = ['canons']
url_list = urldf['canons'].tolist()
url_list = [x.encode("utf-8") for x in url_list]
url_list = [x for x in url_list if str(x).startswith("/")] #filter http snippet
sublists = [url_list[start:start+50000] for start in range(0, len(url_list), 50000)]


def sitemap_gen(counter, sublist):
    outfile_name = "{0}{1}_sitemap_{2:02d}.xml".format(country.lower(), sitemap_type, counter+1)
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset.set("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
    for item in sublist:
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")

        #switch following lines depending on whether input is /canon or www.indeed.com/canon
        full = base + item
        loc.text = full.decode("utf-8")
        #loc.text = item[0]

        """
        #mobile alt url handling
        if len(item) > 1:
            xhtml = ET.SubElement(url, "xhtml:link")
            xhtml.set("rel", "alternate")
            xhtml.set("media", "handheld")
            xhtml.set("href", base + item[1])
        else:
            print raw_input("{0} has no mobile alternate URL! Is that expected? ".format(item[0]))
        """
    tree = ET.ElementTree(urlset)
    tree.write(outfile_name, encoding="UTF-8", xml_declaration=True)
    return outfile_name


def sitemap_index_gen(sitemap_list, outfile_name):
    sitemapindex = ET.Element("sitemapindex")
    sitemapindex.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    for sitemap_file in sitemap_list:
        sitemap = ET.SubElement(sitemapindex, "sitemap")
        loc = ET.SubElement(sitemap, "loc")
        loc.text = sitemap_file + ".gz"
    tree = ET.ElementTree(sitemapindex)
    tree.write(outfile_name, encoding="UTF-8", xml_declaration=True)

sitemap_files = []
for counter, sublist in enumerate(sublists):
    outfile = sitemap_gen(counter, sublist)
    sitemap_files.append("{0}/{1}".format(base, outfile))
    subprocess.call(['gzip', '-9', outfile])
for filename in sorted(sitemap_files):
    print filename
sitemap_index_gen(sitemap_files, sitemap_index_outfile)
