from lxml import etree
import sys

tree = etree.parse(sys.argv[1])

root = tree.getroot()

print(etree.tostring(root, pretty_print=True))

