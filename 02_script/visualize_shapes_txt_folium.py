import folium
import branca.colormap as cm
import webbrowser

m = folium.Map(tiles="cartodbpositron")

colormap = cm.linear.Set1_09.scale(0, 35).to_step(10)
colormap.caption = "A colormap caption"
svg_style = '<style>svg {background-color: white;}</style>'

m.get_root().header.add_child(folium.Element(svg_style))
colormap.add_to(m)

m.save('map.html')
webbrowser.open('map.html')