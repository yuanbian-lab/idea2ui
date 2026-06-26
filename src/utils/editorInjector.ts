export function getEditorScript(): string {
  return `<script>
(function(){
  var c=0,s=null,d=null,m={};
  function g(e){var a=e.getAttribute("data-e");if(!a){a="e"+(++c);e.setAttribute("data-e",a);}return a;}
  function p(t,d){window.parent.postMessage({type:t,data:d},"*");}
  function l(e){
    if(e===document.body||e===document.documentElement)return;
    if(s&&s!==e)s.style.outline="";
    var a=g(e);s=e;e.style.outline="2px solid #1677ff";
    var w=getComputedStyle(e);
    p("editor:select",{
      eid:a,tag:e.tagName,text:(e.textContent||"").substring(0,50),
      styles:{
        background:e.style.background||w.background,
        backgroundColor:e.style.backgroundColor||w.backgroundColor,
        borderRadius:e.style.borderRadius||w.borderRadius,
        color:e.style.color||w.color,
        fontSize:e.style.fontSize||w.fontSize,
        width:e.offsetWidth,height:e.offsetHeight
      },
      transform:e.style.transform||""
    });
  }
  document.addEventListener("mouseover",function(e){
    if(e.target===document.body||e.target===document.documentElement||e.target===s)return;
    e.target.style.outline="1px dashed rgba(22,119,255,0.35)";
  });
  document.addEventListener("mouseout",function(e){
    if(e.target===document.body||e.target===document.documentElement||e.target===s)return;
    e.target.style.outline="";
  });
  document.addEventListener("click",function(e){e.preventDefault();e.stopPropagation();l(e.target);});
  document.addEventListener("mousedown",function(e){
    if(e.target!==s)return;
    d={sx:e.clientX,sy:e.clientY,ox:0,oy:0};
    var t=s.style.transform;
    if(t&&t.indexOf("translate")>=0){
      t=t.replace("translate(","").replace(")","");
      var pts=t.split(",");
      if(pts.length===2){d.ox=parseFloat(pts[0]);d.oy=parseFloat(pts[1]);}
    }
    e.preventDefault();
  });
  document.addEventListener("mousemove",function(e){
    if(!d||!s)return;
    var x=d.ox+e.clientX-d.sx,y=d.oy+e.clientY-d.sy;
    s.style.transform="translate("+x+"px,"+y+"px)";
    s.style.position=s.style.position||"relative";
    s.style.zIndex="100";
    var a=g(s);if(!m[a])m[a]={};m[a].transform=s.style.transform;
    p("editor:drag",{eid:a,transform:s.style.transform,x:x,y:y});
  });
  document.addEventListener("mouseup",function(){d=null;});
  window.addEventListener("message",function(e){
    if(e.data.type==="editor:apply"){
      var el=document.querySelector('[data-e="'+e.data.eid+'"]');
      if(!el)return;
      for(var p in e.data.properties){
        if(!e.data.properties.hasOwnProperty(p))continue;
        if(p==="textContent")el.textContent=e.data.properties[p];
        else el.style[p]=e.data.properties[p];
      }
      var id=e.data.eid;if(!m[id])m[id]={};Object.assign(m[id],e.data.properties);
    }
    if(e.data.type==="editor:getHtml"){
      var h=document.body.innerHTML;
      p("editor:html",{html:h});
    }
    if(e.data.type==="editor:applyAll"){
      for(var id in e.data.modifications){
        if(!e.data.modifications.hasOwnProperty(id))continue;
        var el=document.querySelector('[data-e="'+id+'"]');
        if(!el)continue;
        for(var p in e.data.modifications[id]){
          if(!e.data.modifications[id].hasOwnProperty(p))continue;
          if(p==="textContent")el.textContent=e.data.modifications[id][p];
          else el.style[p]=e.data.modifications[id][p];
        }
      }
    }
  });
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",function(){p("editor:ready",{});});
  else p("editor:ready",{});
})();
</script>`
}
