/* ---------- play: "Wait your turn" ----------
   A small story game. You make a candidate, meet Quorum (a Capitol pigeon), pick a real 2017 member's seat, then walk through the four real elections (2018-2024).
   Every outcome is real: DB.game[bioguide] = [first year in Congress, seat label, first Congress gone from that chamber (0 = never), who took the seat, moved to the other chamber].
   The character, the pigeon and the dialogue are made up; no number is.
   Look: cross stitch on a soft photo. Everything on the stage is a chart of stitches on one grid ('gcv'); nothing is drawn as vectors.
   A sprite is {w,h,cells:[[col,row,v,color]]} where v is 2 for a full cross and 1 for a half stitch. */
const GAME=(()=>{
const E=id=>document.getElementById(id),esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]);
const TH='#f7f0df',DK='#161d27',PHOTO={out:'game-assets/game-bg/dusk.jpg',room:'United_States_House_of_Representatives_chamber.jpg'},
  WALK=['game-assets/game-bg/dome.jpg','game-assets/game-bg/crowd.jpg','game-assets/game-bg/archives.jpg','National Mall - Reflecting Pool (45885661671).jpg','game-assets/game-bg/dusk.jpg'], // the photo behind each stretch of the walk: Capitol, a DC street, a polling place, the Mall, the Mall at dusk
  purl=f=>f.startsWith('game-assets/')?`url("${f}")`:`url("https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(f)}?width=1600")`;
const SK=['#f6dcc6','#e8bc97','#cf9668','#a06a3f','#70482a'],HC=['#3b332d','#7a4f2a','#c9ad3b','#e98dca','#45a86f','#d9d6ce','#9e63d6'],OC=['#c9ad3b','#45a86f','#e98dca','#9e63d6','#ae6c18','#f08a3c','#f7f0df'];
const OPT={hair:['Short','Bob','Long','Curls','Bun','Buzz','None'],fit:['Suit','Skirt suit','Dress','Vest'],extra:['None','Glasses','Bow tie','Pearls','Pin','Briefcase'],face:['Smile','Game face','Smirk','Wow']};
const C={name:'',by:1992,skin:1,hair:1,hc:0,fit:0,oc:3,extra:0,face:0};
const G={run:0,wx:0,pick:null,shown:115,ring:null,started:false,mode:'title',char:false,bird:false,talk:false,walk:false,vote:null,sew:0,year:2017,dirty:true,raf:0,tick:-1,cv:[],lit:null,cap:''};
const V={cell:9,cols:0,rows:0,gy:0,cx:0};
const PC=[116,117,118,119],PMIN={H:25,S:30},STOP={room:70,e:[150,230,310,390],cap:480}; // world positions, in stitches
const inC={};[115,...PC].forEach(c=>inC[c]=new Map(DB.data[c].map(r=>[r[0],r])));
const NEWM={};PC.forEach(c=>NEWM[c]=DB.data[c].filter(r=>!inC[c-1].has(r[0])));
const M115=[...ROSTERS[115].H,...ROSTERS[115].S].filter(Boolean),STILL=M115.filter(m=>inC[119].has(m.bg)).length;
// the game's milestone is 75 or older. n75: how many members that Congress. SUCC: the age of every brand-new member who took a seat a 2017 member left (same seat number), 2019 to 2025.
const OLD=75,n75=c=>DB.data[c].filter(r=>r[8]>=OLD).length,SUCC=[];
Object.values(DB.game).forEach(g=>{const su=g[2]&&g[3]&&inC[g[2]].get(g[3]);if(su)SUCC.push(su[8])});SUCC.sort((a,b)=>a-b);
const line75=c=>{const n=n75(c),o=n75(115),y=startYear(c);return `${n} members ${y===2025?'were':'are'} 75 or older${y===2025?' in 2025':''}, ${n>o?'up from':n<o?'down from':'the same as'} ${o} in 2017.`};
const page=c=>startYear(c)-C.by,chName=k=>k==='H'?'House':'Senate';
const sleep=ms=>new Promise(r=>setTimeout(r,RM.matches?0:ms));
const pc=()=>GC[gi(C.by)],rnd=i=>{const x=Math.sin(i*127.1)*43758.5453;return x-Math.floor(x)};

/* ---- stitches ---- */
const STAMP=new Map(); // one small pre-drawn image per thread color, stitch type, size and wobble, so a frame is only drawImage calls
function stamp(color,v,cell,k){const key=color+v+'|'+cell+'|'+k;let c=STAMP.get(key);if(c)return c;
  const d=devicePixelRatio||1,pad=Math.ceil(cell*.3),s=cell+pad*2;c=document.createElement('canvas');c.width=c.height=Math.ceil(s*d);const x=c.getContext('2d');x.scale(d,d);x.translate(pad,pad);
  // ASCII look (Nov 17): every cell is one typed character. A full stitch is # and a half stitch is +, so shapes and letters stay readable.
  const n=parseInt(color.slice(1),16),dark=color.length===7&&(n>>16)*.3+(n>>8&255)*.59+(n&255)*.11<90; // dark characters get a pale halo so they read on a dark photo
  x.shadowColor=dark?'rgba(247,240,223,.7)':'rgba(0,0,0,.6)';x.shadowBlur=cell*(dark?.3:.22);x.shadowOffsetY=dark?0:cell*.07;x.fillStyle=color;
  x.font=`500 ${cell*1.3}px "IBM Plex Mono",ui-monospace,monospace`;x.textAlign='center';x.textBaseline='middle';x.globalAlpha=v===2?1:.85;
  x.fillText(v===2?'#':'+',cell/2,cell*.54);
  c.pad=pad;c.s=s;STAMP.set(key,c);return c}
const put=(x,X,Y,v,col,cell)=>{const s=stamp(col,v,cell,(X*7+Y*13&3));x.drawImage(s,X*cell-s.pad,Y*cell-s.pad,s.s,s.s)};
// chart: rows of characters. '.' is empty, a lowercase letter is a full cross in pal[letter], uppercase is a half stitch.
function chart(rows,pal){const cells=[];rows.forEach((r,y)=>[...r].forEach((ch,x)=>{if(ch==='.'||ch===' ')return;const lo=ch.toLowerCase(),col=pal[lo];if(col)cells.push([x,y,ch===lo?2:1,col])}));return{w:Math.max(...rows.map(r=>r.length)),h:rows.length,cells}}
const FONT={'+':'044v440',A:'ehhvhhh',B:'uhhuhhu',C:'ehggghe',D:'uhhhhhu',E:'vgguggv',F:'vgguggg',G:'ehgnhhf',H:'hhhvhhh',I:'e44444e',J:'72222ic',K:'hikokih',L:'ggggggv',M:'hrllhhh',N:'hpljhhh',O:'ehhhhhe',P:'uhhuggg',Q:'ehhhlid',R:'uhhukih',S:'fgge11u',T:'v444444',U:'hhhhhhe',V:'hhhhha4',W:'hhhllla',X:'hha4ahh',Y:'hha4444',Z:'v1248gv',
  0:'ehhhhhe',1:'4c4444e',2:'eh1248v',3:'v2421he',4:'26aiv22',5:'vgu11he',6:'68guhhe',7:'v124888',8:'ehhehhe',9:'ehhf12c','?':'eh12404','!':'4444404','.':'0000004','-':'000e000'};
const TXT=new Map();
function text(str,col=TH){const key=str+col;if(TXT.has(key))return TXT.get(key);const cells=[],L=String(str).toUpperCase().split('|');let w=0; // '|' starts a new line
  L.forEach((l,li)=>{w=Math.max(w,l.length*6-1);[...l].forEach((ch,ci)=>{const g=FONT[ch];if(!g)return;for(let r=0;r<7;r++){const b=parseInt(g[r],32);for(let k=0;k<5;k++)if(b>>(4-k)&1)cells.push([ci*6+k,li*9+r,2,col])}})});
  const sp={w,h:L.length*9-2,cells};TXT.set(key,sp);return sp}
const flip=(sp,fx,fy)=>({w:sp.w,h:sp.h,cells:sp.cells.map(([x,y,v,c])=>[fx?sp.w-1-x:x,fy?sp.h-1-y:y,v,c])});
function drawSp(cv,sp,cell,grid){const d=devicePixelRatio||1;cv.width=sp.w*cell*d;cv.height=sp.h*cell*d;cv.style.width=sp.w*cell+'px';cv.style.height=sp.h*cell+'px';
  if(grid){cv.classList.add('ggrid');cv.style.setProperty('--cell',cell+'px')}const x=cv.getContext('2d');x.scale(d,d);sp.cells.forEach(([c,r,v,col])=>put(x,c,r,v,col,cell))}

/* ---- charts ---- */
const P0={w:TH,d:DK,g:'#c3c9cc',y:'#e3b94a',t:'#b08a5c',l:'#7fc79a'};
const CORNER=chart(['www.ww.','w.w.w..','www....','...w...','ww..w.w','w....w.','....w.w'],P0),CORNERS=[CORNER,flip(CORNER,1,0),flip(CORNER,0,1),flip(CORNER,1,1)];
const CAP={};Object.entries(DB.stitch).forEach(([w,rows])=>CAP[w]=chart(rows,P0)); // the Capitol, charted from the illustration at a few widths (pipeline/build_stitch_capitol.py)
const LAMP=chart(['.yyy.','yyyyy','yyyyy','.yyy.','..g..','..g..','..g..','..g..','..g..','..g..','..g..','..g..','..g..','..g..','.ggg.'],P0);
const TREE=chart(['...lll...','..lllLL..','.llllLLL.','lllllLLLL','lllllLLLL','.llllLLL.','..lllLL..','....t....','....t....','....t....','....t....','....t....'],P0);
const BENCH=chart(['wwwwwwwwwwww','............','wwwwwwwwwwww','.g........g.','.g........g.'],P0);
const BALLOT=chart(['www','www'],P0);
const boxSp=a=>chart(['...wwwww...','wwwwwwwwwww','w.........w','w..a...a..w','w...a.a...w','w....a....w','w...a.a...w','w..a...a..w','wwwwwwwwwww'],{w:TH,a});
// the door to the chamber, where you meet the seats
const DOOR=chart(['...........w...........','.........wwWww.........','.......wwWWWWWww.......','.....wwWWWWWWWWWww.....','...wwWWWWWWWWWWWWWww...','.wwwwwwwwwwwwwwwwwwwww.','.ggggggggggggggggggggg.','..w.w..ttttttttt..w.w..','..w.w..tTTTtTTTt..w.w..','..w.w..tTTTtTTTt..w.w..','..w.w..tTTTtTTTt..w.w..','..w.w..tTTTtTTTt..w.w..','..w.w..ttttttttt..w.w..','..w.w..tTTTtTTTt..w.w..','..w.w..tTTytyTTt..w.w..','..w.w..tTTTtTTTt..w.w..','..w.w..tTTTtTTTt..w.w..','..w.w..tTTTtTTTt..w.w..','..w.w..ttttttttt..w.w..','.ggggggggggggggggggggg.','ggggggggggggggggggggggg'],P0);
function signSp(t){const s=text(t),w=s.w+4,cells=s.cells.map(([x,y,v,c])=>[x+2,y+2,v,c]);
  for(let x=0;x<w;x++)cells.push([x,0,1,TH],[x,10,1,TH]);for(let y=1;y<10;y++)cells.push([0,y,1,TH],[w-1,y,1,TH]);for(let y=11;y<17;y++)cells.push([w>>1,y,2,P0.t]);return{w,h:17,cells}}
const BIRD=['...www........','...www........','...aaa........','..wwwww.......','...gggg.......','.yygdgg.......','...gggg.......','...aagggg.....','...ggggggggg..','...gggGGGGggg.','....ggGGGGgggg','.....ggggggg..','......y..y....','.....yy.yy....'];
const birdSp=open=>chart(BIRD.map((r,i)=>open&&i===6?'.yy'+r.slice(3):r),{...P0,a:pc()});
// the candidate: a 16 x 27 chart built in layers (head, outfit, face, hair, extra). Big head, small body, formal wear.
const HEAD=['................','................','................','....ssssssss....','...ssssssssss...','..ssssssssssss..','..ssssssssssss..','..ssssssssssss..','..sssdssssdsss..','..sssdssssdsss..','..sbbssssssbbs..','..ssssssssssss..','...ssssssssss...','....ssssssss....','.......ss.......'];
const LEGS=c=>[...Array(4).fill('....'+c.repeat(3)+'..'+c.repeat(3)+'....'),'....kkk..kkk....'],SKIRT=['.....ss..ss.....','.....ss..ss.....','....kkk..kkk....'];
const FIT={Suit:['....oowwwwoo....','...ooowaawooo...','...oooOaaOooo...','...oooOaaOooo...','...oooooooooo...','...soooooooos...','....oooooooo....',...LEGS('o')],
  'Skirt suit':['....oowwwwoo....','...ooowwwwooo...','...ooooOOoooo...','...oooooooooo...','...oooooooooo...','...soooooooos...','....oooooooo....','....oooooooo....','...oooooooooo...',...SKIRT],
  Dress:['....oooooooo....','...sooowwooos...','...soooooooos...','...saaaaaaaas...','...soooooooos...','...soooooooos...','...oooooooooo...','..oooooooooooo..','..oooooooooooo..',...SKIRT],
  Vest:['....wwowwoww....','...wwooaaooww...','...wwooaaooww...','...wwooaaooww...','...wwooooooww...','...s.oooooo.s...','.....oooooo.....',...LEGS('p')]};
const TOP={2:'....hhhhhhhh....',3:'...hhhhhhhhhh...',4:'..hhhhhhhhhhhh..',5:'..hhhhhhhhhhhh..'},SIDE='.hh..........hh.',BOB={...TOP,6:'.hhhhhhhhhhhhhh.',7:'.hhh.h....h.hhh.',8:SIDE,9:SIDE,10:SIDE,11:SIDE,12:SIDE,13:'..hh........hh..'};
const HAIR={Short:{...TOP,6:'..hhhhhhhh...h..',7:'..hhh...........'},Bob:BOB,Long:{...BOB,13:SIDE,14:SIDE,15:SIDE,16:SIDE,17:SIDE,18:SIDE},
  Curls:{1:'...hh.hhhh.hh...',2:'..hhhhhhhhhhhh..',3:'.hhhhhhhhhhhhhh.',4:'hhhhhhhhhhhhhhhh',5:'hhhhhhhhhhhhhhhh',6:'hhhh.hh..hh.hhhh',7:'hhh..........hhh',8:'hhh..........hhh',9:SIDE,10:'.h............h.'},
  Bun:{...TOP,0:'......hhhh......',1:'.....hhhhhh.....',6:'..hhhhhhhhhhhh..',7:'..h..........h..'},Buzz:{2:'....HHHHHHHH....',3:'...HHHHHHHHHH...',4:'..HHHHHHHHHHHH..',5:'..HH........HH..'},None:{}};
const EXTRA={None:{},Glasses:{8:'....wdwWWwdw....',9:'....wdw..wdw....'},'Bow tie':{15:'.....aawwaa.....'},Pearls:{15:'.....WWWWWW.....'},Pin:{17:'..........a.....'},Briefcase:{20:'.............tt.',21:'............tttt',22:'............tttt'}};
const FACE={Smile:{11:'.......dd.......'},'Game face':{7:'....dd....dd....',11:'......dddd......'},Smirk:{11:'........ddd.....'},Wow:{11:'.......dd.......',12:'.......dd.......'}};
const CHS=new Map();
function charSp(c,frame=0,blink=false,head=false){const key=[c.skin,c.hair,c.hc,c.fit,c.oc,c.extra,c.face,c.by,frame,blink,head].join();if(CHS.has(key))return CHS.get(key);
  const rows=[...HEAD,...FIT[OPT.fit[c.fit]]].map(r=>[...r]),lay=o=>Object.entries(o).forEach(([y,s])=>[...s].forEach((ch,x)=>{if(ch!=='.')rows[y][x]=ch}));
  if(blink){rows[8][5]='s';rows[8][10]='s'}
  lay(FACE[OPT.face[c.face]]);lay(HAIR[OPT.hair[c.hair]]);lay(EXTRA[OPT.extra[c.extra]]);
  if(frame){const a=frame===1?9:4;for(let x=a;x<a+3;x++){rows[26][x]='.';rows[25][x]='k'}} // one foot lifted
  const oc=OC[c.oc],a=pc()===oc?TH:pc(),sp=chart((head?rows.slice(0,14):rows).map(r=>r.join('')),{s:SK[c.skin],h:HC[c.hc],o:oc,a,w:TH,d:DK,b:'#e79aa0',p:'#b9bfc4',k:TH,t:'#b08a5c'});
  if(CHS.size>400)CHS.clear();CHS.set(key,sp);return sp}
// a member's portrait: bright areas are full crosses, mid-tones are half stitches in the generation color, dark areas are left open
function faceSp(bg,by,n){const g=(n===24?GRID:GRID2)[bg],h=n*1.25,cells=[],col=GC[gi(by)];
  for(let y=0;y<h;y++)for(let x=0;x<n;x++){if(g){const l=g[y*n+x];if(l>150)cells.push([x,y,2,TH]);else if(l>96)cells.push([x,y,1,col])}
    else if(((x-n/2+.5)/(n*.3))**2+((y-h*.42)/(h*.3))**2<1||y>h*.76&&Math.abs(x-n/2+.5)<n*.42)cells.push([x,y,1,col])} // no portrait: a plain silhouette
  return{w:n,h,cells}}

/* ---- stage ---- */
let WORLD=[];
let BGI=0;
function scene(i){const a=[E('gbg'),E('gbgx')],n=a[1-BGI],im=purl(WALK[i]);if(a[BGI].style.backgroundImage===im)return; // crossfade the two outdoor layers
  n.style.backgroundImage=im;n.style.opacity=1;a[BGI].style.opacity=0;BGI=1-BGI}
function build(){const gs=E('gs');
  E('gbg').style.backgroundImage=purl(PHOTO.out);E('gbg2').style.backgroundImage=purl(PHOTO.room);WALK.forEach(f=>{new Image().src=purl(f).slice(5,-2)});
  WORLD.push({x:STOP.room+26,sp:DOOR});
  STOP.e.forEach((x,r)=>WORLD.push({x:x+44,sp:signSp(String(startYear(PC[r])-1))},{x:x+27,r}));
  WORLD.push({x:STOP.cap+26,sp:BENCH});
  const taken=[...WORLD.map(p=>[p.x-3,p.x+(p.sp?p.sp.w:11)+3]),...[0,STOP.room,...STOP.e,STOP.cap].map(x=>[x-11,x+27])],free=(x,w)=>taken.every(([a,b])=>x+w<a||x>b); // lamps and trees only where nothing else stands
  for(let x=38;x<560;x+=40){const sp=x%80===38?LAMP:TREE;if(free(x,sp.w))WORLD.push({x,sp})}
  new ResizeObserver(()=>{size();pdraw();const p=E('gpv');if(p)prev()}).observe(gs)}
function size(){const gs=E('gs'),W=gs.clientWidth,T=parseFloat(getComputedStyle(gs).getPropertyValue('--top'))||0,H=gs.clientHeight-T;if(!W||H<=0)return; /* --top: room kept clear under the site header */
  const cell=Math.max(6,Math.min(10,Math.floor(W/112))),cols=Math.floor(W/cell),rows=Math.floor(H/cell),d=devicePixelRatio||1,cv=E('gcv'),ox=(W-cols*cell)>>1,oy=T+((H-rows*cell)>>1);
  Object.assign(V,{ox,oy,cell,cols,rows,gy:rows-Math.ceil((W<700?214:178)/cell),cx:Math.round(cols*.2)});
  cv.width=cols*cell*d;cv.height=rows*cell*d;cv.style.cssText=`width:${cols*cell}px;height:${rows*cell}px;left:${ox}px;top:${oy}px;--cell:${cell}px`;
  gs.style.setProperty('--hx',ox+3*cell+'px');gs.style.setProperty('--hy',oy+12*cell+'px');G.dirty=true}
// the ending picture: everyone who took an opened seat, in three age groups. One figure (a head stitch over a body stitch) per person; your group is in your color.
const GROUPS=[['Under 35',a=>a<35],['35 to 49',a=>a<50],['50 or older',()=>true]].map(([t,f],i,all)=>({t,n:SUCC.filter(a=>f(a)&&!all.slice(0,i).some(g=>g[1](a))).length}));
const myGroup=a=>a<35?0:a<50?1:2;
function crowdGeo(){const {cols,cell}=V,side=G.side&&cols>=96,avail=side?cols-Math.ceil(440/cell)-6:cols-8,per=Math.max(12,Math.min(40,avail>>1)),lab=Math.ceil(24/cell);let y=12+Math.ceil(50/cell);
  const rows=GROUPS.map(g=>{const r={...g,ly:y,y:y+lab};y+=lab+Math.ceil(g.n/per)*3+1;return r});return{side,per,x0:4,rows}}
function crowdKey(){const on=G.mode==='crowd'&&!E('gs').classList.contains('inroom'),k=E('gkey'),ax=E('gax');k.hidden=ax.hidden=!on;if(!on)return;
  const g=crowdGeo(),{ox,oy,cell}=V,me=myGroup(G.crowd),key=[g.per,cell,ox,oy,G.crowd,g.side].join();if(k.dataset.k===key)return;k.dataset.k=key;
  k.innerHTML=`<b>Who took the open seats</b><span>Each figure is one new member who took a seat that a 2017 member left, 2019 to 2025.</span>`;k.style.maxWidth=Math.max(250,g.per*2*cell)+'px';
  ax.style.cssText=`left:${ox+g.x0*cell}px;top:${oy}px`;
  ax.innerHTML=g.rows.map((r,i)=>`<span style="top:${r.ly*cell}px${i===me?';color:'+pc():''}">${r.t} · ${r.n}${i===me?` · you ${g.side||true?'at '+G.crowd:''}`:''}</span>`).join('')}
function items(now){crowdKey();let on75=false;const {cols,rows,gy,cx}=V,it=[],t=RM.matches?0:Math.floor(now/160);
  const corners=()=>CORNERS.forEach((sp,i)=>it.push({sp,x:i&1?cols-7:0,y:i&2?rows-7:0}));
  if(G.mode==='title'){const ts=text(cols>=96?'WAIT YOUR TURN':'WAIT|YOUR|TURN'),top=8,room=rows-top-Math.ceil(126/V.cell)-ts.h-3;
    const w=[84,70,56,44].find(w=>w<=cols-12&&CAP[w].h<=room)||44,cp=CAP[w],y=top+Math.max(0,room-cp.h>>1);
    corners();it.push({sp:ts,x:cols-ts.w>>1,y:y+cp.h+3},{sp:cp,x:cols-cp.w>>1,y})}
  else if(E('gs').classList.contains('inroom'));
  else if(G.mode==='world'){const w0=Math.floor(G.wx),sx=x=>cx+x-w0;
    it.push({sp:text(String(G.year)),x:3,y:3});
    if(G.char&&G.year>=2017){const c=Math.min(119,115+Math.floor((G.year-2017)/2)),n=n75(c),b=n75(115),per=18,y0=cols>=96?5:24,X=i=>cols-3-per*2+(i%per)*2+1,Y=i=>y0+(i/per|0)*2,row=(i0,i1)=>{const cs=[];for(let i=i0;i<i1;i++)cs.push([X(i),Y(i),2,TH]);return{w:cols,h:rows,cells:cs}};
      it.push({sp:row(0,Math.min(n,b)),x:0,y:0,a:.5});if(n>b)it.push({sp:row(b,n),x:0,y:0}); // one X per member 75 or older; the ones added since 2017 are brighter
      const l=E('g75'),tx=`${n} members are 75 or older`+(n>b?` · ${n-b} more than in 2017`:'');if(l.textContent!==tx)l.textContent=tx;l.style.cssText=`right:${V.ox+3*V.cell}px;top:${V.oy+y0*V.cell-22}px`;on75=true}
    if(G.vote){const b=WORLD.find(p=>p.r===G.vote.r);for(let i=0;i<3;i++){const k=(now-G.vote.t0-i*300)/700;if(k>=0&&k<1)it.push({sp:BALLOT,x:sx(b.x)+4,y:gy-21+Math.floor(k*12)})}}
    if(G.char)it.push({sp:charSp(C,G.walk?1+t%2:0,!G.walk&&t%26===0),x:cx-8,y:gy-27});
    if(G.bird)it.push({sp:birdSp(G.talk&&t%2===0),x:cx+10,y:gy-14-(G.walk?t%2:0)});
    WORLD.forEach(p=>{const sp=p.sp||boxSp(pc()),x=sx(p.x);if(x>-sp.w&&x<cols)it.push({sp,x,y:gy-sp.h})});
    const gr=[];for(let x=0;x<cols;x++){gr.push([x,0,1,TH]);if(((x+w0)%8+8)%8<4)gr.push([x,2,1,TH])}it.push({sp:{w:cols,h:3,cells:gr},x:0,y:gy,a:.6});}
  else if(G.mode==='crowd'){const g=crowdGeo(),me=myGroup(G.crowd),cs=[],mine=[];
    g.rows.forEach((r,i)=>{const L=i===me?mine:cs,col=i===me?pc():TH;for(let k=0;k<r.n;k++){const x=g.x0+(k%g.per)*2,y=r.y+(k/g.per|0)*3;L.push([x,y,2,col],[x,y+1,i===me?2:1,col])}});
    it.push({sp:{w:cols,h:rows,cells:mine},x:0,y:0},{sp:{w:cols,h:rows,cells:cs},x:0,y:0,a:.85});
    if(!g.side&&g.x0+g.per*2+22<=cols)it.push({sp:charSp(C,0,t%26===0),x:cols-19,y:gy-27});
    const gr=[];for(let x=0;x<cols;x++)gr.push([x,0,1,TH]);it.push({sp:{w:cols,h:1,cells:gr},x:0,y:gy,a:.6});}
  else corners();
  E('g75').hidden=!on75;return it}
function render(now){const {cols,rows,cell}=V,cv=E('gcv');if(!cols)return;const x=cv.getContext('2d'),d=devicePixelRatio||1,occ=new Uint8Array(cols*rows),list=[];
  x.setTransform(d,0,0,d,0,0);x.clearRect(0,0,cols*cell,rows*cell);
  items(now).forEach(o=>o.sp.cells.forEach(([c,r,v,col])=>{const X=o.x+c,Y=o.y+r;if(X<0||Y<0||X>=cols||Y>=rows||occ[Y*cols+X])return;occ[Y*cols+X]=1;list.push([X,Y,v,col,o.a||1])})); // front items claim their cells first
  let n=list.length;if(G.sew){const p=RM.matches?1:Math.min(1,(now-G.sew)/1500);list.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);n=Math.ceil((1-(1-p)*(1-p))*n);if(p>=1)G.sew=0}
  for(let i=0;i<n;i++){const s=list[i];x.globalAlpha=s[4];put(x,s[0],s[1],s[2],s[3],cell)}x.globalAlpha=1}
function loop(now){if(E('v-play').hidden){G.raf=0;return}const tick=Math.floor(now/160);
  if(G.dirty||G.walk||G.sew||G.vote||tick!==G.tick){G.tick=tick;G.dirty=false;render(now)}G.raf=requestAnimationFrame(loop)}
const sew=()=>{G.sew=performance.now();G.dirty=true};
function setWx(x){G.wx=x;E('gbg').style.translate=E('gbgx').style.translate=`${-x/STOP.cap*5}% 0`;G.dirty=true}
function setYear(y){G.year=y;E('gage').innerHTML=`<span class="gsr">${y}, </span>Age ${y-C.by}`;G.dirty=true}
// the running record under the year: what you have done, and how many in the 2025 Congress list the same thing
const rec=()=>{E('grec').innerHTML=G.cv.length?'<span class="mono">Your record</span>'+G.cv.map(v=>`<div><span>${v.d.slice(0,-1)}</span><b>${v.n}</b></div>`).join('')+'<small>number in the 2025 Congress</small>':''};
const tint=()=>{E('gs').style.setProperty('--pc',pc());G.dirty=true};
function walk(to,year){return new Promise(res=>{const run=G.run,from=G.wx,dur=RM.matches?0:Math.min(3200,Math.abs(to-from)*32);
  if(!dur){setWx(to);if(year)setYear(year);return res()}
  G.walk=true;const t0=performance.now();let ticked=false;
  const step=now=>{if(run!==G.run){G.walk=false;return}const p=Math.min(1,(now-t0)/dur),e=p<.5?2*p*p:1-(-2*p+2)**2/2;setWx(from+(to-from)*e);
    if(year&&!ticked&&p>.5){ticked=true;setYear(year)}
    if(p<1)requestAnimationFrame(step);else{G.walk=false;G.dirty=true;res()}};requestAnimationFrame(step)})}

/* ---- dialogue: typewriter text, tap anywhere to finish the line, then pick a button ---- */
function say(who,text,choices=['Next']){return new Promise(res=>{const run=G.run,box=E('gdlg'),t=E('gtext'),ch=E('gchoice');
  box.hidden=false;E('gwho').textContent=who;E('gsr').textContent=who+': '+text;ch.innerHTML='';t.textContent='';let i=0,done=false,iv=0;
  G.talk=who==='Quorum';
  const fin=()=>{if(done)return;done=true;clearInterval(iv);t.textContent=text;G.talk=false;G.dirty=true;
    ch.innerHTML=choices.map((c,j)=>`<button class="${j||choices.length>1?'':'pbtn'}" data-j="${j}">${esc(c)}</button>`).join('');ch.querySelector('button').focus({preventScroll:true})};
  box.onclick=e=>{const b=e.target.closest('button[data-j]');if(b){box.onclick=null;res(+b.dataset.j)}else fin()};
  if(RM.matches)fin();else iv=setInterval(()=>{if(run!==G.run)return clearInterval(iv);i++;t.textContent=text.slice(0,i);if(i>=text.length)fin()},20)})}
const q=(t,c)=>say('Quorum',t,c),hideDlg=()=>E('gdlg').hidden=true;
function over(html,cls=''){const o=E('gover');o.className='gover '+cls;o.innerHTML=html;o.hidden=false;o.onclick=null;o.scrollTop=0;E('gs').classList.toggle('inroom',cls==='room'||cls==='end');G.dirty=true;paint();
  if(cls!=='create'){const b=o.querySelector('.pbtn');if(b)b.focus({preventScroll:true})}}
const unover=()=>{E('gover').hidden=true;E('gover').innerHTML='';E('gs').classList.remove('inroom');G.dirty=true};
// stitched pieces inside cards: <canvas data-t="TEXT">, <canvas data-f="bioguide"> (portrait) and <canvas data-you> (your face)
// one X per person who took an opened seat, stacked by age. Those your age or younger are in your color.
function histSp(you){const lo=SUCC[0],hi=SUCC[SUCC.length-1],n={},cells=[];let top=0;SUCC.forEach(a=>{n[a]=(n[a]||0)+1;top=Math.max(top,n[a])});
  for(let a=lo;a<=hi;a++)for(let k=0;k<(n[a]||0);k++)cells.push([a-lo,top-1-k,2,a<=you?pc():TH]);return{w:hi-lo+1,h:top,cells}}
const phist=you=>`<p>${SUCC.length} new members took a seat that opened between 2019 and 2025. ${GROUPS[0].n} were under 35, ${GROUPS[1].n} were 35 to 49 and ${GROUPS[2].n} were 50 or older.</p>`;
function paint(){document.querySelectorAll('#gover canvas[data-q]').forEach(cv=>drawSp(cv,birdSp(true),4,false));
  document.querySelectorAll('#gover canvas[data-h]').forEach(cv=>{const sp=histSp(+cv.dataset.h),w=cv.parentElement.clientWidth||300;drawSp(cv,sp,Math.max(3,Math.min(7,Math.floor(w/sp.w))),true)});
  document.querySelectorAll('#gover canvas[data-t],#gover canvas[data-f],#gover canvas[data-you]').forEach(cv=>{const d=cv.dataset,cell=+d.c||4;
  drawSp(cv,d.t?text(d.t,d.col==='pc'?pc():TH):d.f?faceSp(d.f,+d.by,+d.n):charSp(C,0,false,true),cell,!d.t)})}
const st=(t,c=4,col='')=>`<canvas data-t="${esc(t)}" data-c="${c}" data-col="${col}" role="img" aria-label="${esc(String(t).replace(/\|/g,' '))}"></canvas>`;

/* ---- scenes ---- */
function titleScene(){return new Promise(res=>{G.mode='title';sew();
  over(`<div class="gtitle"><span class="mono">A game about getting into Congress</span><div><button class="pbtn" data-act="go">New game</button><span class="mono">Real members · real elections · 2017 to 2025</span></div></div>`,'title');
  E('gover').onclick=e=>{if(e.target.closest('[data-act=go]'))res()}})}
function prev(){const p=E('gpv');if(!p)return;drawSp(p,charSp(C),Math.max(6,Math.min(13,Math.floor(p.parentElement.clientHeight/27))),true)}
function creator(){return new Promise(res=>{G.mode='blank';G.dirty=true;
  const cyc=(k,t)=>`<div class="gcyc" data-k="${k}"><span class="mono">${t}</span><button data-d="-1" aria-label="Previous ${t}">‹</button><b></b><button data-d="1" aria-label="Next ${t}">›</button></div>`;
  const sw=(k,t,a)=>`<div class="gsw" data-k="${k}" role="group" aria-label="${t}"><span class="mono">${t}</span>${a.map((c,i)=>`<button style="background:${c}" data-i="${i}" aria-label="${t} ${i+1}"></button>`).join('')}</div>`;
  over(`<div class="gcreate"><div class="gprev"><canvas id="gpv" aria-hidden="true"></canvas></div><div class="gctl"><span class="mono">Make your candidate</span>${st('WHOS RUNNING?',3)}
    <div class="gfield"><label>Name <input id="gname" maxlength="14" placeholder="Your name" value="${esc(C.name)}" autocomplete="off"></label><span class="mono">Age 25 in 2017</span></div>
    ${cyc('hair','Hair')}${sw('hc','Hair color',HC)}${sw('skin','Skin color',SK)}${cyc('fit','Outfit')}${sw('oc','Outfit color',OC)}${cyc('extra','Extra')}${cyc('face','Face')}
    <div class="prow" style="margin-top:6px"><button data-act="shuffle">Shuffle</button><button class="pbtn" data-act="ready">Ready</button></div></div></div>`,'create');
  const o=E('gover'),draw=()=>{tint();prev();
    o.querySelectorAll('.gcyc').forEach(d=>d.querySelector('b').textContent=OPT[d.dataset.k][C[d.dataset.k]]);
    o.querySelectorAll('.gsw button').forEach(b=>b.setAttribute('aria-pressed',C[b.parentElement.dataset.k]===+b.dataset.i))};
  o.oninput=e=>{if(e.target.id==='gname')C.name=e.target.value.trim()};
  o.onclick=e=>{const b=e.target.closest('button');if(!b)return;const k=b.parentElement.dataset.k;
    if(b.dataset.d){const n=OPT[k].length;C[k]=(C[k]+ +b.dataset.d+n)%n}
    else if(b.dataset.i)C[k]=+b.dataset.i;
    else if(b.dataset.act==='shuffle'){const r=n=>Math.floor(Math.random()*n);Object.assign(C,{skin:r(5),hair:r(7),hc:r(7),fit:r(4),oc:r(7),extra:r(6),face:r(4)})}
    else if(b.dataset.act==='ready'){o.oninput=null;return res()}
    draw()};
  draw()})}

/* the chamber as a sampler: one cross per seat, in that member's generation thread */
let PSE=[];
function pdraw(){const cv=E('pcv');if(!cv)return;const w=cv.parentElement.clientWidth;if(!w)return;const d=devicePixelRatio||1,x=cv.getContext('2d');
  cv.width=Math.round(w*d);cv.height=Math.round(w*AR*d);cv.style.height=w*AR+'px';const k=w/1000*d;x.setTransform(k,0,0,k,0,0);
  const c=G.shown,nw=c>115?new Set(NEWM[c].map(r=>r[0])):null;PSE=[];
  ["H","S"].forEach(s=>SEATS[s].forEach((p,i)=>PSE.push({x:p.x,y:p.y,w:DIM[s][0],h:DIM[s][1],m:ROSTERS[c][s][i]})));
  let hit=null;x.lineCap='round';
  PSE.forEach(s=>{const m=s.m;if(!m)return;const lit=G.lit?G.lit(m)||m.bg===G.ring:!nw||nw.has(m.bg)||m.bg===G.ring,a=s.w*.36,b=s.h*.36;
    x.globalAlpha=lit?1:.22;x.strokeStyle=lit?GC[m.g]:TH;x.lineWidth=s.w*.2;x.beginPath();x.moveTo(s.x-a,s.y+b);x.lineTo(s.x+a,s.y-b);x.moveTo(s.x-a,s.y-b);x.lineTo(s.x+a,s.y+b);x.stroke();if(m.bg===G.ring)hit=s});
  x.globalAlpha=1;
  if(hit){x.strokeStyle=TH;x.lineWidth=2.2;x.beginPath();x.ellipse(hit.x,hit.y,hit.w/2+4,hit.h/2+4,0,0,7);x.stroke();
    x.lineWidth=1.4;x.setLineDash([5,4]);x.beginPath();x.arc(hit.x,hit.y,30,0,7);x.stroke();x.setLineDash([])}
  E('pcap').textContent=G.lit?G.cap:c===115?`2017 · ${M115.length} members · all seats taken`:`${startYear(c)} · ${NEWM[c].length} new members lit`;if(E('gtip'))E('gtip').textContent=G.tip||'';
}
const fyou=()=>`<canvas data-you="1" data-c="4" aria-hidden="true"></canvas>`;
const fmem=(bg,by,n)=>`<canvas data-f="${bg}" data-by="${by}" data-n="${n}" data-c="4" aria-hidden="true"></canvas>`;
const band=(k,t,x='',c=4)=>`<div class="pband"><span class="mono">${k}</span>${x}<h2>${st(t,c)}</h2></div>`,body=h=>`<div class="pbody">${h}</div>`;
const pwho=(m,age)=>`<div class="pwho">${fmem(m.bg,m.by,24)}<div><b>${m.name}</b><span>${m.st} · ${chName(m.ch)} · age ${age}</span><span>In Congress since ${DB.game[m.bg][0]}${since(DB.game[m.bg][0])}</span></div></div>`;
const since=y=>{const d=C.by-y;return d>1?`, ${d} years before you were born`:d===1?', the year before you were born':d===0?', the year you were born':`, when you were ${-d}`};
const pdots=(r,done)=>`<div class="pdots" aria-hidden="true">${PC.map((c,i)=>`<span class="${i<r||(i===r&&done)?'done':i===r?'now':''}">${startYear(c)-1}</span>`).join('')}</div>`;
const pvs=(c,m)=>`<div class="pvs"><div>${fyou()}<div><b>${page(c)}</b><span>You</span></div></div><i>vs</i><div>${fmem(m.bg,m.by,12)}<div><b>${inC[c].get(m.bg)[8]}</b><span>Them</span></div></div></div>`;
const pvsu=(c,su)=>`<div class="pvs"><div>${fyou()}<div><b>${page(c)}</b><span>You</span></div></div><i>vs</i><div>${fmem(su[0],su[6],12)}<div><b>${su[8]}</b><span>Took the seat</span></div></div></div>`;
// one sourced event from the generation timeline, the one closest to the year this member was your starting age (25). Their real age that year is shown.
const then=m=>{const a0=2017-C.by,f=DB.tl.filter(f=>f[2]>=m.by).sort((x,y)=>Math.abs(x[2]-m.by-a0)-Math.abs(y[2]-m.by-a0)||(y[0]===m.g)-(x[0]===m.g))[0];return f&&Math.abs(f[2]-m.by-a0)<=6?{y:f[2],a:f[2]-m.by,t:f[3]}:null};
const newLine=c=>{const n=NEWM[c];return `${n.length} new members arrived that year. Their median age was ${fmt(med(n.map(r=>r[5])))}.`};
const room=`<div class="groom"><div class="pstage"><canvas id="pcv" role="img" aria-label="The chamber. Use the buttons in the panel to pick a seat."></canvas><p class="pcap mono" id="pcap"></p><div class="gtip"><canvas data-q="1" aria-hidden="true"></canvas><p id="gtip"></p></div></div><div class="ppanel" id="ppanel"></div></div>`;
function pickSeat(){return new Promise(res=>{G.shown=115;G.ring=null;G.pick=null;G.lit=x=>x.yrs>=OLD;G.cap=`2017 · ${n75(115)} of ${M115.length} members are 75 or older`;G.tip=`Bright seats are the ${n75(115)} members who are 75 or older. Grey seats are everyone else. You can pick any of them.`;over(room,'room');const cv=E('pcv');cv.classList.add('pickable');
  const draw=()=>{const m=G.pick;E('ppanel').innerHTML=band('Pick a seat','WHOSE SEAT?')+body(`<p>Tap a seat, or:</p><div class="prow"><button data-act="old">Pick one for me</button><button data-act="oldest">The oldest member</button></div>
    ${m?pwho(m,m.yrs)+`<button class="pbtn" data-act="wait">Wait for this seat</button>`:''}`);paint();pdraw()};
  const set=m=>{G.pick=m;G.ring=m.bg;draw();const b=E('ppanel').querySelector('.pbtn');if(b)b.focus({preventScroll:true})};
  cv.onclick=e=>{const r=cv.getBoundingClientRect(),x=(e.clientX-r.left)/r.width*1000,y=(e.clientY-r.top)/r.width*1000;let best=null,bd=18;
    PSE.forEach(s=>{if(!s.m)return;const dd=Math.hypot(s.x-x,s.y-y);if(dd<bd){bd=dd;best=s.m}});if(best)set(best)};
  E('ppanel').onclick=e=>{const b=e.target.closest('[data-act]');if(!b)return;const a=b.dataset.act;
    if(a==='wait')return res(G.pick);const s=[...M115].sort((x,y)=>x.by-y.by||y.age-x.age);
    const o=M115.filter(x=>x.yrs>=OLD&&x!==G.pick),rnd=l=>l[Math.floor(Math.random()*l.length)];set(a==='oldest'?s[0]:a==='old'?rnd(o):rnd(M115))};
  draw()})}
const took=su=>`<div class="pwho">${fmem(su[0],su[6],24)}<div><span>The seat went to</span><b>${su[1]}</b><span>age ${su[8]}</span></div></div>`;
function result(c,m,r){return new Promise(res=>{const g=DB.game[m.bg],y=startYear(c)-1,open=g[2]===c;G.shown=c;G.lit=null;G.tip=`Bright seats are the ${NEWM[c].length} members who are new this year.${open&&g[3]?' The ringed one took your seat.':''}`;G.ring=open?(g[3]||null):m.bg;over(room,'room');let h;
  if(!open){const n=NEWM[c],k=n.filter(x=>x[8]<=page(c)).length,w=page(c)-PMIN[m.ch];G.tip=`Bright seats are the ${n.length} members who are new this year. ${k===0?'None are':k===1?'1 is':k+' are'} your age or younger. The ringed seat is the one you are waiting for.`;
    h=band(`After the ${y} election`,String(y),pdots(r,true),6)+body(`<div class="pstamp">${st('STILL THERE',3)}</div>${pvs(c,m)}<p><b>${m.name}</b> is still in office.${w>0?` You have been old enough for this seat for ${w} year${w>1?'s':''}.`:''}</p><p>${line75(c)}</p>
    <button class="pbtn" data-act="go">${r===3?'Walk to the Capitol':'Keep walking'}</button>`)}
  else{const su=g[3]&&inC[c].get(g[3]);
    h=band(`After the ${y} election`,g[1],pdots(r,true))+body(`<div class="pstamp">${st('SEAT OPEN',3,'pc')}</div>
    <p><b>${m.name}</b> ${g[4]?'moved to the '+chName(m.ch==='H'?'S':'H'):'is no longer in the '+chName(m.ch)}. They had been in Congress since ${g[0]}.</p>
    ${su?pvsu(c,su)+`<p>The seat went to <b>${su[1]}</b>, a new member.</p>`:`<p>No brand-new member took this exact seat. ${newLine(c)}</p>`}
    <button class="pbtn" data-act="go">Walk to the Capitol</button>`)}
  const P=E('ppanel');P.innerHTML=h;P.classList.add('pflip');paint();pdraw();P.querySelector('.pbtn').focus({preventScroll:true});
  P.onclick=e=>{if(e.target.closest('[data-act=go]'))res()}})}
// the look-back list on the result card: each choice with its real count, and what each election did to your seat
const hist=(m,out)=>{const rows=[];G.cv.forEach((v,r)=>{const c=PC[r];rows.push([v.y,`${v.d} <i>${v.f}</i>`],[startYear(c)-1,`Election. ${c===out?'The seat opened.':m.name.replace(/\.$/,'')+' stayed.'} <i>${n75(c)} members 75 or older, you were ${page(c)}.</i>`])});
  return `<details class="ghis"><summary class="mono">Look back at your ${2*G.cv.length} years</summary><div class="gline">${rows.map(([y,t])=>`<b class="mono">${y}</b><span>${t}</span>`).join('')}</div></details>`};
function poster(m,out){const g=DB.game[m.bg],su=out&&g[3]&&inC[out].get(g[3]),a=out?page(out):page(119),min=PMIN[m.ch];
  const end=`<div class="prow"><button class="pbtn" data-act="ff">Fast forward</button><button data-act="again">Try another seat</button></div>`;
  over(`<div class="ppanel gposter">${out?band(`${startYear(out)} · ${g[1]}`,'SEAT|OPEN','',6)+body(`${su?pvsu(out,su):''}
      <p>You waited ${startYear(out)-2017} years for <b>${m.name}</b>'s seat.${su?` It went to <b>${su[1]}</b>, ${su[8]>a?(su[8]-a)+' years older than you':su[8]<a?(a-su[8])+' years younger than you':'your age'}.`:` ${newLine(out)}`}${a<min?` The ${chName(m.ch)} needs ${min}.`:''}</p>${phist(a)}${hist(m,out)}${end}`)
    :band('2025 · 8 years later','STILL|WAITING','',6)+body(`${pvs(119,m)}<p><b>${m.name}</b> never left. You went from ${2017-C.by} to ${a}. ${line75(119)}</p>${phist(a)}${hist(m,out)}${end}`)}</div>`,'gside');G.side=true;G.dirty=true;
  E('gover').onclick=e=>{const b=e.target.closest('[data-act]');if(!b)return;const k=b.dataset.act;if(k==='ff')return future();play('again')}}

// the ending: your years laid out, and the 2025 chamber with everyone born before you lit. Only arithmetic: the constitutional minimum ages and the 2025 medians. No prediction.
function future(){const R=[...ROSTERS[119].H,...ROSTERS[119].S].filter(Boolean),by=C.by,older=R.filter(x=>x.by<by).length,rows=G.cv.map(v=>[v.y,`${v.d} <i>${v.f}</i>`]);
  [['House',25],['Senate',30]].forEach(([n,min])=>{let e=by+min-1;if(e%2)e++;rows.push([e,e<=2024?`You are old enough for the ${n} from this election on.`:`The first election that could seat you in the ${n}. It needs ${min}.`])});
  [[med(NEWM[119].map(r=>r[5])),'members who were new in 2025'],[med(DB.data[119].map(r=>r[5])),'all of Congress in 2025']].forEach(([x,w])=>{const y=by+Math.ceil(x);rows.push([y,`${y<=2025?'You passed':'You reach'} ${fmt(x)}, the median age of ${w}.`])});
  rows.sort((a,b)=>a[0]-b[0]);
  Object.assign(G,{shown:119,ring:null,lit:x=>x.by<by,cap:`2025 · ${older} of ${R.length} members were born before you`,tip:`Bright seats are members born before you. Grey seats are members your age or younger.`});over(room,'room');
  const P=E('ppanel');P.innerHTML=band('Your years','FAST|FORWARD')+body(`<div class="gline">${rows.map(([y,t])=>`<b class="mono">${y}</b><span>${t}</span>`).join('')}</div>
    <div class="prow"><button class="pbtn" data-act="again">Try another seat</button><button data-act="new">New character</button><button data-act="explore">Explore the chamber</button></div>`);
  paint();pdraw();P.onclick=e=>{const b=e.target.closest('[data-act]');if(!b)return;const k=b.dataset.act;if(k==='explore')return showView('chamber');play(k==='again'?'again':'title')}}
// what you do between elections: [button, what you did, the count as shown in the on-screen record, the count as a sentence. Counts are from the CRS profile of the 119th Congress (R48535, updated Aug 4 2025, from members' own CQ profiles)].
// The step is a made-up example. The count is real. Nothing here changes the outcome, and no odds are attached.
const MEAN=[['Intern on Capitol Hill','Interned on Capitol Hill','91+','At least 91 people in the 2025 Congress once worked as congressional staff.'],
   ['Join AmeriCorps','Joined AmeriCorps','3','3 members of the 2025 Congress were AmeriCorps volunteers. 2 were in the Peace Corps.'],
   ['Go to law school','Went to law school','31% of House','31% of the House and 47% of the Senate in 2025 have law degrees and practiced law.'],
   ['Run for school board','Ran for school board','387','305 House members and 82 senators in 2025 held elected office before Congress.'],
   ['Run for state legislature','Ran for state legislature','251','251 members of the 2025 Congress served in a state or territorial legislature.'],
   ['Run for mayor','Ran for mayor','38','38 members of the 2025 Congress were mayors.'],
   ['Organize a union','Organized a union','5','5 House members in 2025 were union representatives.'],
   ['Start a business','Started a business','163+','At least 135 House members and 28 senators in 2025 owned, founded or ran a business.']];
async function play(mode){
  const run=++G.run,ok=async p=>{const v=await p;if(run!==G.run)throw 0;return v};
  try{
    scene(0);setWx(0);tint();hideDlg();E('ghud').hidden=true;E('gs').classList.remove('play');G.cv=[];rec();G.cv=[];G.lit=null;G.side=false;Object.assign(G,{char:false,bird:false,walk:false,talk:false,vote:null});
    if(mode!=='again'){await ok(titleScene());await ok(creator())}
    unover();tint();Object.assign(G,{mode:'world',char:true,bird:true});E('gs').classList.add('play');E('ghud').hidden=false;setYear(2017);sew();
    const a=2017-C.by;
    if(mode==='again')await ok(q('Back again. Pick a different seat this time.'));
    else{
      await ok(q('Coo. You look new.'));
      await ok(q(`I'm Quorum. I live on the Capitol roof.`));
      await ok(q(`So${C.name?', '+C.name:''}, you want a seat in Congress.`));
      await ok(q('There are 535 of them. Every one is taken.'));
      await ok(q(a<25?`You're ${a}. The House won't take you until 25. The Senate, 30.`:a<30?`You're ${a}. Just old enough for the House. The Senate wants 30.`:`You're ${a}. Old enough for either chamber. That part is done.`));
      await ok(q("Around here, you wait your turn. Come on, I'll show you the room.",["Let's go"]));
    }
    hideDlg();await ok(walk(STOP.room));
    await ok(q('This is everyone seated on January 3, 2017. Real people, real ages.'));
    await ok(q("Pick one. That's the seat you'll wait for.",['Open the chamber']));
    hideDlg();const m=await ok(pickSeat()),g=DB.game[m.bg];unover();
    await ok(q(`${m.name.replace(/\.$/,'')}. Age ${m.yrs}, in Congress since ${g[0]}${g[0]<C.by?'. You were born in '+C.by:''}.`));
    const ev=then(m);if(ev){G.year=ev.y;E('gage').textContent=`They are ${ev.a}`;G.dirty=true;
      await ok(q(`Picture ${ev.y}. They are ${ev.a}${ev.a===a?', your age':', about your age'}.`));await ok(q(`${ev.t}.`));setYear(2017);await ok(q(`Now it's 2017 again. They are ${m.yrs}. You are ${a}.`))}
    await ok(q(m.yrs>=OLD?`One of ${n75(115)} members who are 75 or older. Let's see how long they stay.`:m.yrs>=60?`${m.yrs}. Mid-career around here. This could take a while.`:`${m.yrs}. Young for this room. This could take a long while.`,['Start walking']));
    let out=0;const STAY=[()=>'Still there. Keep walking.',c=>`Still there. You're ${page(c)} now, by the way.`,()=>'Three elections. Same person. Coo.',()=>'Four for four.'];
    for(let r=0;r<4;r++){const c=PC[r],y=startYear(c)-1,young=page(c)<PMIN[m.ch];
      const yr=2017+2*r,pool=MEAN.filter(p=>!G.cv.some(v=>v.d===p[1]+'.')).slice(0,3);
      const pk=await ok(q(r?'Two more years until the next one. What now?':'The next election is two years off. What will you do?',pool.map(p=>p[0])));
      G.cv.push({y:yr,d:pool[pk][1]+'.',n:pool[pk][2],f:pool[pk][3]});rec();await ok(q(pool[pk][3]));
      hideDlg();scene(r+1);await ok(walk(STOP.e[r],y));
      await ok(q((r===0?`${y}. Election day. Every House seat is up, and a third of the Senate.`:`${y}. Election day again.`)+(young?` You'd be ${page(c)} at swearing-in. Too young for the ${chName(m.ch)}.`:''),[`Hold the ${y} election`]));
      hideDlg();G.vote={r,t0:performance.now()};await ok(sleep(1500));G.vote=null;setYear(startYear(c));
      await ok(result(c,m,r));unover();
      if(g[2]===c){out=c;break}
      await ok(q(STAY[r](c)));
    }
    hideDlg();scene(0);await ok(walk(STOP.cap));
    if(out){const su=g[3]&&inC[out].get(g[3]),a2=page(out),min=PMIN[m.ch];
      await ok(q(`The seat opened in ${startYear(out)}.`));
      await ok(q(su?`It went to ${su[1]}, age ${su[8]}.`:newLine(out)));
      await ok(q(a2<min?`You were ${a2}. The ${chName(m.ch)} needs ${min}. Not your turn yet.`:`You were ${a2}. Old enough to run. Whether you'd win, I can't say. I'm a pigeon.`));
    }else{
      await ok(q(`It's 2025. ${m.name} is ${inC[119].get(m.bg)[8]} and still in that seat.`));
      await ok(q(`You were ${a} when we met. You're ${page(119)} now.`));
      await ok(q(`${STILL} of the ${M115.length} members from 2017 are still here. Coo.`));
    }
    {const ya=out?page(out):page(119);hideDlg();E('ghud').hidden=true;G.crowd=ya;G.mode='crowd';sew();await ok(sleep(900));
      await ok(q(`So who did get in? These are the ${SUCC.length} new members who took a seat that opened, 2019 to 2025.`));
      await ok(q(`${GROUPS[0].n} were under 35. ${GROUPS[1].n} were 35 to 49. ${GROUPS[2].n} were 50 or older.`));
      await ok(q(`${out?'You were':"You're"} ${ya}. Your group is the one in your color.`,['See my result']))}
    hideDlg();poster(m,out);
  }catch(e){if(e!==0)throw e}
}
build();
/* A small looping snippet of the game for the Play hub: the candidate and Quorum walking while the four election years go by. */
function preview(cv){const W=56,H=38,YRS=['2018','2020','2022','2024'];let t=0,last=0;
  const frame=()=>{const cells=[],add=(sp,x,y)=>sp.cells.forEach(c=>{const X=c[0]+x,Y=c[1]+y;if(X>=0&&X<W&&Y>=0&&Y<H)cells.push([X,Y,c[2],c[3]])});
    const sp=text(YRS[(t/84|0)%4]);add(sp,W-(t%84),2);
    for(let x=0;x<W;x++)if((x+t)%5)cells.push([x,H-2,1,TH]);
    add(charSp(C,RM.matches?0:1+t%2,false),12,H-29);add(birdSp(false),32,H-16-(t%2));
    const cell=Math.max(3,Math.floor(cv.parentElement.clientWidth/W));drawSp(cv,{w:W,h:H,cells},cell,false)};
  if(RM.matches){t=30;frame();return}
  if(cv._on)return;cv._on=1;
  (function loop(now){if(!cv.isConnected||!cv.offsetParent){cv._on=0;return}if(now-last>170){last=now;t++;frame()}requestAnimationFrame(loop)})(0)}
return{preview,title(cv,t,cell){drawSp(cv,text(t),cell,false)},capitol(cv,maxW,maxH){const ks=Object.keys(CAP).map(Number).sort((x,y)=>y-x);let pick=ks[ks.length-1],cell=3;for(const k of ks){const c=Math.floor(Math.min(maxW/CAP[k].w,maxH/CAP[k].h));if(c>=5){pick=k;cell=c;break}}cv._cap={sp:CAP[pick],cell};drawSp(cv,CAP[pick],cell,false)},capCells(cv){return cv._cap?{n:cv._cap.sp.cells.length,w:cv._cap.sp.w,h:cv._cap.sp.h,cell:cv._cap.cell,at:i=>cv._cap.sp.cells[i]}:null},capDraw(cv,hot){const k=cv._cap;if(!k)return;const d=devicePixelRatio||1,x=cv.getContext('2d'),{sp,cell}=k;x.setTransform(d,0,0,d,0,0);x.clearRect(0,0,cv.width,cv.height);x.textAlign='center';x.textBaseline='middle';x.font=`500 ${cell*1.3}px "IBM Plex Mono",ui-monospace,monospace`;sp.cells.forEach(([c,r,v,col],i)=>{const h=hot&&hot.get(i);if(h){x.globalAlpha=1-h.a;put(x,c,r,v,col,cell);x.globalAlpha=h.a;x.fillStyle=h.col;x.fillText(h.ch,c*cell+cell/2,r*cell+cell*.54)}else put(x,c,r,v,col,cell)});x.globalAlpha=1},enter(){size();if(!G.started){G.started=true;play('title')}pdraw();if(!G.raf)G.raf=requestAnimationFrame(loop);},C,G,V,play};
})();
