MTK is a tool set for map navigation developers, which includes the functions of drawing and picking up points, lines and polygons, inquiring and drawing NDS tiles and mercator tiles, displaying in WKT/WKB format and geojson format, wgs84/gcj02 coordinate system transfer, etc.

geometry visualization
你可以输入一些格式为x1,y1,x2,y2,x3,y3的点串，选择以点、线或者面的形式进行绘制

坐标拾取
你可以在canvas上以点、线或者面的形式绘制一些图形，左键绘制，右键作为multilinestring 或者 multipolygon的分隔，连续右键作为结束，拾取一些坐标点，这些坐标也会以geojson和wkt的形式存储在geojson wkt标签栏

nds瓦片绘制
你可以输入一些nds格式的瓦片号进行绘制，也可以选择瓦片level后获取当前视野下所有的瓦片，勾选dynamic draw后可以随着视野的变化动态显示这些瓦片

mercator瓦片绘制
你可以输入一些mercator格式的瓦片号进行绘制，也可以选择瓦片level后获取当前视野下所有的瓦片，勾选dynamic draw后可以随着视野的变化动态显示这些瓦片

wkt绘制
你可以输入一些符合wkt/wkb格式的字符串，把这些geometry进行绘制

geojson绘制
你可以输入一些符合geojson格式的字符串，把这些geometry进行绘制

coordinate transform
你可以将gcj02/wgs84/web mecator三种坐标系之间的坐标随意进行转换

xyz layer
你可以添加一些常用的栅格瓦片进行使用