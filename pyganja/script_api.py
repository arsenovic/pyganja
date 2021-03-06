
from __future__ import print_function

from IPython.display import display, Javascript

import os
from .GanjaScene import GanjaScene
import base64
from multiprocessing import Process


try:
    from .cefwindow import *
except:
    print('Failed to import cef_gui, cef functions will be unavailable')


def html_to_data_uri(html):
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    ret = "data:text/html;base64,{data}".format(data=b64)
    return ret


def read_ganja():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    ganja_filename = dir_name + '/static/ganja.js/ganja.js'
    with open(ganja_filename, 'r') as ganja_file:
        output = ganja_file.read()
    return output


def generate_notebook_js(script_json, layout, grid=True, scale=1.0):
    
    p=(layout.sig>0).sum()
    q=(layout.sig<0).sum()

    sig = '%i,%i'%(p,q)
    mv_length = str(2**layout.dims)
    
    # not the best way to test conformal, as it prevents non-euclidean  geometry
    conformal = False
    if q!=0:
        conformal=True

    if sig in ['4,1','3,0','3,1','2,0']:
        if grid:
            gridstr = 'true'
        else:
            gridstr = 'false'
        scalestr = str(scale)
        js = read_ganja()
        js += """
        function add_graph_to_notebook(Algebra){
            var output = Algebra("""+sig+""",()=>{
              // When we get a file, we load and display.
                var canvas;
                var h=0, p=0;
                  // convert arrays of floats back to CGA elements.     
                     var data = """ + script_json + """;
                     data = data.map(x=>x.length=="""+mv_length+"""?new Element(x):x);
                  // add the graph to the page.
                     canvas = this.graph(data,{gl:true,conformal:"""+str(conformal).lower()+""",grid:"""+gridstr+""",scale:"""+scalestr+"""});
                     canvas.options.h = h; canvas.options.p = p;
                  // make it big.
                     canvas.style.width = '50vw';
                     canvas.style.height = '50vh';
                     return canvas;
                }
            );
            element.append(output);
        }
        require(['Algebra'],function(Algebra){add_graph_to_notebook(Algebra)});
        """
    else:
        raise ValueError('Algebra not yet supported')
    return js


def generate_full_html(script_json, algebra='g3c', grid=True, scale=1.0):
    if grid:
        gridstr = 'true'
    else:
        gridstr = 'false'
    scalestr = str(scale)
    script_string = """
            Algebra(4,1,()=>{
              var canvas = this.graph((""" + script_json + """).map(x=>x.length==32?new Element(x):x),
              {conformal:true,gl:true,grid:"""+gridstr+""",scale:"""+scalestr+"""});
              canvas.style.width = '100vw';
              canvas.style.height = '100vh';
              document.body.appendChild(canvas);
            });
            """
    full_html = """<!DOCTYPE html>
    <html lang="en" style="height:100%;">
    <HEAD>
        <meta charset="UTF-8">
        <title>pyganja</title>
        <link rel="stylesheet" href="static/pyganja.css">
      <SCRIPT>""" + read_ganja() + """</SCRIPT>
    </HEAD>
    <BODY style="position:absolute; top:0; bottom:0; right:0; left:0; overflow:hidden;">
    <SCRIPT>
        """ + script_string + """
    </SCRIPT>
    </BODY>
    </html>
    """
    return full_html


def render_notebook_script(script_json, layout, grid=True, scale=1.0):
    """
    In a notebook we dont need to start cefpython as we
    are already in the browser!
    """
    js = generate_notebook_js(script_json, layout=layout, grid=grid, scale=scale)
    display(Javascript(js))


def render_cef_script(script_json="", grid=True, scale=1.0):
    def render_script():
        final_url = html_to_data_uri(generate_full_html(script_json, grid=grid, scale=scale))
        run_cef_gui(final_url, "pyganja")
    p = Process(target=render_script)
    p.start()
    p.join()


def draw(objects, color=int('AA000000', 16), grid=True, scale=1.0):
    if isinstance(objects, list):
        sc = GanjaScene()
        sc.add_objects(objects, color=color)
        layout= objects[0].layout # not the best
        render_notebook_script(str(sc), layout=layout, grid=grid, scale=scale)
    else:
        raise ValueError('The input is not a list of objects')


def draw_objects(objects, color=int('AA000000', 16), grid=True, scale=1.0):
    if isinstance(objects, list):
        sc = GanjaScene()
        sc.add_objects(objects, color=color)
        render_cef_script(str(sc), grid=grid, scale=scale)
    else:
        raise ValueError('The input is not a list of objects')
