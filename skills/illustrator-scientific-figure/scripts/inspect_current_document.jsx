// Nonmodal read-only probe. DoJavaScript returns JSON; manual execution writes to the console.
function figureJson(v) {
    if (v === null || v === undefined) return 'null';
    if (typeof v === 'number') return isFinite(v) ? String(v) : 'null';
    if (typeof v === 'boolean') return String(v);
    if (typeof v === 'string') {
        return '"'+v.replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/[\x00-\x1f]/g,function(c){
            return '\\u'+('0000'+c.charCodeAt(0).toString(16)).slice(-4);
        })+'"';
    }
    var a=[],k;
    if(v instanceof Array){for(k=0;k<v.length;k++)a.push(figureJson(v[k]));return '['+a.join(',')+']';}
    for(k in v)if(v.hasOwnProperty(k))a.push(figureJson(k)+':'+figureJson(v[k]));
    return '{'+a.join(',')+'}';
}
function inspectScientificDocument(d) {
    var unavailable=[];
    function read(key,fn){try{return fn();}catch(e){unavailable.push(key);return null;}}
    var r={status:'INSPECTED_ONLY',version:String(app.version),name:String(d.name),
        fullName:read('fullName',function(){return d.fullName.fsName;}),
        colorSpace:read('documentColorSpace',function(){return String(d.documentColorSpace);}),
        colorProfile:read('colorProfileName',function(){return String(d.colorProfileName);}),
        artboards:[],textFrames:[],placedItems:[],counts:{},unavailable:unavailable,
        font_substitution:'NOT_VERIFIED',scientific_review:'NOT_PERFORMED',visual_review:'NOT_PERFORMED'};
    var keys=['layers','pageItems','pathItems','groupItems','textFrames','placedItems','rasterItems'];
    for(var k=0;k<keys.length;k++)r.counts[keys[k]]=read(keys[k],function(){return d[keys[k]].length;});
    for(var i=0;i<d.artboards.length;i++)r.artboards.push({name:d.artboards[i].name,rect:d.artboards[i].artboardRect});
    for(i=0;i<d.textFrames.length;i++){
        var t=d.textFrames[i],fonts={},sizes={};
        for(var j=0;j<t.characters.length;j++){
            var c=t.characters[j].characterAttributes;
            var f=read('font',function(){return c.textFont.name;});if(f!==null)fonts[f]=true;
            var s=read('fontSize',function(){return c.size;});if(s!==null)sizes[String(s)]=true;
        }
        var names=[],points=[];for(var n in fonts)if(fonts.hasOwnProperty(n))names.push(n);
        for(n in sizes)if(sizes.hasOwnProperty(n))points.push(Number(n));
        r.textFrames.push({index:i,contents:t.contents,bounds:t.visibleBounds,fonts:names,sizes:points});
    }
    for(i=0;i<d.placedItems.length;i++){
        var p=d.placedItems[i];r.placedItems.push({index:i,name:p.name,
            file:read('placed.file',function(){return p.file.fsName;}),
            fileExists:read('placed.file.exists',function(){return p.file.exists;}),bounds:p.visibleBounds});
    }
    return r;
}
// ENTRYPOINT
(function(){
    if(app.documents.length===0)throw new Error('No active document');
    var output=figureJson(inspectScientificDocument(app.activeDocument));$.writeln(output);return output;
}());
