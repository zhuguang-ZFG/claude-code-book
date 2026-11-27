"""Screen rules for the shell, structure pages, TOC, part dividers and chapters."""
from __future__ import annotations

SCREEN_CSS = r"""*{box-sizing:border-box}
@media (prefers-reduced-motion: no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--paper);color:var(--ink);
  font:400 17px/1.8 var(--serif);
  font-feature-settings:"kern" 1,"liga" 1,"palt" 1;
  font-kerning:normal;text-rendering:optimizeLegibility;
  -webkit-font-smoothing:antialiased}
/* the ground is paper, not a flat browser field: three very soft washes keep
   the sheet warm without becoming a grain that fights the ink. Screen only —
   print resets `background` wholesale — and dark mode keeps the falloff but
   drops the warm tint so the drawing stays the thing you look at. */
@media screen{
  body{background-attachment:fixed;background-image:
    radial-gradient(58rem 44rem at 16% -6%,rgba(180,71,47,.04),transparent 70%),
    radial-gradient(50rem 40rem at 94% 18%,rgba(200,164,92,.055),transparent 68%),
    radial-gradient(62rem 50rem at 52% 106%,rgba(67,57,43,.032),transparent 72%)}
}
@media screen and (prefers-color-scheme:dark){
  body:not(.force-light){background-attachment:fixed;background-image:
    radial-gradient(58rem 44rem at 16% -6%,rgba(224,123,95,.028),transparent 70%),
    radial-gradient(62rem 50rem at 52% 106%,rgba(0,0,0,.16),transparent 72%)}
}
body.lang-en{font-family:"Iowan Old Style",Palatino,Georgia,var(--serif);
  line-height:1.75;font-size:17px}
/* book blocks: flush both edges; CJK breaks strictly, Latin hyphenates */
.chapter-body p,.chapter-body li{text-align:justify}
.chapter-body p{text-wrap:pretty}
body.lang-zh .chapter-body p,body.lang-zh .chapter-body li,
body.lang-zh .chapter-body blockquote{line-break:strict;hanging-punctuation:allow-end}
body.lang-en .chapter-body p,body.lang-en .chapter-body li{hyphens:auto}
/* ragged-right beats a grid of gaps once the line is short enough that one
   unbreakable token costs the whole row its spacing -- see the contract test */
@media (max-width:30rem){body.lang-zh .chapter-body p,body.lang-zh .chapter-body li{text-align:left}}
::selection{background:rgba(180,71,47,.16)}
@media (prefers-color-scheme:dark){
  body:not(.force-light) ::selection{background:rgba(224,123,95,.26)}}
a{color:inherit}
a.ext::after{content:"↗";font-size:.72em;vertical-align:.15em;
  margin-inline:.12em .2em;color:var(--bronze);font-family:var(--sans)}
a.xref{color:var(--bronze-3);text-decoration:none;
  border-bottom:1px dotted var(--bronze-2);
  transition:color .14s ease,border-bottom-color .14s ease}
a.xref:hover{color:var(--cinnabar);border-bottom-color:var(--cinnabar)}
h1,h2,h3,h4{font-family:var(--sans);font-weight:700;line-height:1.35;
  color:var(--ink);letter-spacing:.01em;text-wrap:balance}

/* ------- shell & rail ------- */
.sheet{max-width:calc(var(--measure) + 4rem);margin:0 auto;padding:0 2rem}
/* A wide screen splits the column in two widths — see the reading-column rule
   at the end of this sheet, which has to come last because every component
   below sets its own `margin` shorthand. */
nav.rail{display:none;position:fixed;inset:0 auto 0 0;width:17rem;
  overflow-y:auto;background:var(--paper-2);border-right:1px solid var(--line);
  padding:1.6rem 1.1rem 3rem;font-family:var(--sans);font-size:.82rem;
  scrollbar-width:thin}
/* the wide-screen block has to come after the base rule above: `nav.rail` and
   `nav.rail` are equally specific, so a media query written first simply loses
   and the reader gets the reserved gutter with no rail in it */
@media (min-width:1360px){
  body{padding-left:17.5rem}
  .sheet{max-width:var(--furniture)}
  nav.rail{display:block}
}
nav.rail .rail-title{font-size:.72rem;letter-spacing:.35em;color:var(--bronze);
  text-transform:uppercase;margin:0 0 1rem;display:flex;gap:.5rem;align-items:center}
nav.rail .rail-part{margin:.95rem 0 .25rem;font-weight:700;color:var(--bronze-3);
  font-size:.78rem;letter-spacing:.08em}
/* a twelve-volume omnibus puts 280+ links in the rail; each volume folds into a
   native details block so the reader scans twelve doors, not one long column. */
nav.rail details.rail-vol{margin:.35rem 0 .2rem;border-radius:var(--r-1);
  transition:background-color .15s ease}
nav.rail details.rail-vol[open]{background:rgba(251,247,239,.55);padding-bottom:.35rem}
nav.rail details.rail-vol>summary.rail-part{cursor:pointer;list-style:none;
  display:flex;align-items:baseline;gap:.45rem;margin:0;padding:.28rem .4rem;
  border-radius:var(--r-1);transition:color .14s ease,background-color .14s ease}
nav.rail details.rail-vol>summary.rail-part:hover{color:var(--cinnabar);
  background:var(--paper)}
nav.rail details.rail-vol>summary.rail-part:focus-visible{outline:2px solid var(--cinnabar);
  outline-offset:-2px}
nav.rail details.rail-vol>summary.rail-part::-webkit-details-marker{display:none}
nav.rail details.rail-vol>summary.rail-part::before{content:"▸";
  flex:0 0 auto;color:var(--bronze);font-size:.7rem;transition:transform .14s ease}
nav.rail details.rail-vol[open]>summary.rail-part::before{content:"▾";color:var(--cinnabar)}
nav.rail details.rail-vol>a{padding-left:1.05rem}
nav.rail details.rail-vol>a.rail-part{margin:.45rem 0 .15rem;padding-left:.85rem;
  font-size:.74rem;letter-spacing:.06em;color:var(--bronze)}
@media (prefers-color-scheme:dark){
  body:not(.force-light) nav.rail details.rail-vol[open]{background:rgba(24,24,20,.45)}
}
.collection-jumps{position:sticky;top:0;z-index:20;display:flex;align-items:center;
  flex-wrap:wrap;gap:.55rem 1.2rem;padding:.58rem 0;
  background:rgba(251,247,239,.92);backdrop-filter:blur(8px);
  -webkit-backdrop-filter:blur(8px);border-bottom:1px solid var(--line);
  font-family:var(--sans);font-size:.82rem}
.collection-jumps a{color:var(--bronze-3);text-decoration:none;
  padding:.12rem .45rem;border-radius:var(--r-1);
  transition:color .14s ease,background-color .14s ease}
.collection-jumps a:first-child{font-weight:700;color:var(--ink);
  margin-inline-end:auto;padding-inline-start:0}
.collection-jumps a:hover{color:var(--cinnabar);background:var(--paper-2)}
.collection-jumps a:focus-visible{outline:2px solid var(--cinnabar);outline-offset:1px}
@media (prefers-color-scheme:dark){
  body:not(.force-light) .collection-jumps{background:rgba(24,24,20,.9)}
}
@media screen and (max-width:1359px){
  .collected [id]{scroll-margin-top:3.5rem}
}
@media screen and (max-width:44rem){
  #collection-guide th{white-space:normal}
}
@media screen and (max-width:30rem){
  .collected [id]{scroll-margin-top:5.5rem}}
@media (min-width:1360px){.collection-jumps{display:none}}
nav.rail a{display:block;color:var(--ink-2);text-decoration:none;
  padding:.18rem .55rem;border-left:2px solid transparent;line-height:1.5;
  border-radius:0 var(--r-1) var(--r-1) 0;
  transition:color .14s ease,border-color .14s ease,background-color .14s ease}
nav.rail a:hover{color:var(--cinnabar);border-left-color:var(--cinnabar);
  background:var(--paper)}
nav.rail a:focus-visible{outline:2px solid var(--cinnabar);outline-offset:-2px}
/* the rail's only non-chapter link, wearing the same wheel the route map
   starts with, so the sidebar and the page it jumps to share one sign */
nav.rail .rail-map{display:flex;align-items:center;gap:.45rem;
  color:var(--bronze-3);font-weight:600;margin-bottom:.5rem}
nav.rail .rail-map .rmk{flex:none;width:.8rem;height:.8rem;color:var(--bronze)}

/* ------- structure pages ------- */
.front-page{padding:2.4rem 0 1.9rem}
.page-title{font-size:1.95rem;margin:0 0 1.15rem;color:var(--bronze-3);
  letter-spacing:.04em}
.page-title::after{content:"";display:block;width:4rem;height:3px;
  background:linear-gradient(90deg,var(--cinnabar),var(--bronze-2));
  margin-top:.55rem;border-radius:999px}
section.front-page{break-before:page}
.cover{text-align:center;padding:0;position:relative}
.cover .wheel{width:26px;height:26px;color:var(--bronze-2);opacity:.9;flex:0 0 auto}
/* one frame, not two: the outline used to draw a second line 5px outside the
   border, which at book size reads as a plate that printed twice */
.cover-inner{position:relative;display:inline-block;text-align:center;
  padding:clamp(2.2rem,5vw,4rem) clamp(1.6rem,5vw,4.2rem) 2.6rem;margin:2.4rem 0;
  border:none;
  background:linear-gradient(180deg,var(--card),var(--paper));
  box-shadow:0 18px 42px -28px rgba(38,34,27,.36),
             inset 0 0 0 1px var(--line-2),inset 0 0 0 4px var(--card),
             inset 0 0 0 5.5px var(--bronze-2),inset 0 0 0 6.5px var(--card);
}
@media (prefers-color-scheme:dark){
  body:not(.force-light) .cover-inner{
    box-shadow:0 20px 44px -24px rgba(0,0,0,.78),
               inset 0 0 0 1px var(--line-2),inset 0 0 0 4px var(--card),
               inset 0 0 0 5.5px var(--bronze-2),inset 0 0 0 6.5px var(--card)}
}
.cover-inner::before{content:"";position:absolute;top:0;bottom:0;left:0;
  width:5px;background:linear-gradient(180deg,var(--cinnabar),var(--bronze-2));
  border-radius:0}
.cover-inner::after{content:"";position:absolute;top:0;bottom:0;right:0;
  width:2px;background:linear-gradient(180deg,rgba(180,71,47,.15),rgba(67,57,43,.1));
  pointer-events:none}
.cover-kicker{font-family:var(--sans);font-size:.7rem;letter-spacing:.42em;
  color:var(--bronze);text-transform:uppercase;margin:0 auto 1.6rem;
  max-width:calc(100% - 7.6rem)}
.book-title{margin:0;line-height:1.12;font-weight:750;letter-spacing:.06em}
.bt-main{display:block;font-size:clamp(3.1rem,9vw,4.9rem);letter-spacing:.14em;
  text-indent:.14em;color:var(--ink);font-weight:700;
  font-family:"STSong","Songti SC","Noto Serif SC",var(--serif)}
.bt-tail{display:block;font-family:var(--sans);font-weight:400;font-size:1.2rem;
  letter-spacing:.3em;text-indent:.3em;color:var(--ink-2);margin-top:.9rem}
.cover-seal{position:absolute;top:clamp(1.4rem,4vw,2.6rem);
  right:clamp(1.4rem,4vw,2.6rem);display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:.05rem;width:2.9rem;
  padding:.42rem 0;background:var(--cinnabar);color:var(--paper);
  font-family:var(--kai);font-size:1.05rem;line-height:1.15;letter-spacing:0;
  writing-mode:vertical-rl;border-radius:var(--r-1);transform:rotate(1.8deg);
  box-shadow:inset 0 0 0 2px rgba(251,247,239,.55)}
.cover-seal-latin{writing-mode:horizontal-tb;width:auto;min-width:2.75rem;
  padding:.36rem .5rem;font-family:var(--sans);font-size:.76rem;font-weight:700;
  letter-spacing:.1em;line-height:1.1}
.collected .bt-main{font-size:clamp(2.25rem,5.8vw,3.5rem);letter-spacing:.08em;
  text-indent:.08em;line-height:1.22}
@media (prefers-color-scheme:dark){
  body:not(.force-light) .cover-seal{box-shadow:inset 0 0 0 2px rgba(24,24,20,.45)}
}
@media (max-width:30rem){
  .cover-kicker{max-width:calc(100% - 5.8rem);letter-spacing:.26em}
  .cover-seal{width:2.35rem;font-size:.92rem;padding:.32rem 0;top:1rem;right:1rem}
  .cover-seal-latin{width:auto;min-width:2.2rem;font-size:.66rem;padding:.26rem .38rem}
}
.cover-rule{display:flex;align-items:center;justify-content:center;gap:.9rem;
  margin:1.7rem auto 1.2rem;max-width:26rem}
.cover-rule i{height:1px;flex:1;background:linear-gradient(90deg,transparent,
  var(--bronze-2),transparent)}
.cover-art{width:min(34rem,94%);display:block;margin:.5rem auto 1.6rem;
  color:var(--ink-2)}
.cover-art img{width:100%;height:auto;display:block}
/* Cover micro-labels are decorative texture, not the title: at the real phone
   cover width they render at only 2.9–4.5px. The accessible title and subtitle
   live outside the aria-hidden SVG, so keep the cover quiet instead of printing
   unreadable type. */
.cover-art svg text{display:none}
.book-sub{font-family:var(--sans);font-size:.95rem;color:var(--ink-2);
  margin:0 0 1.8rem;letter-spacing:.1em}
.book-epi{font-family:var(--kai);font-size:1.02rem;color:var(--bronze-3);
  margin:0 auto 1.9rem;line-height:2}
.book-epi .epi-src{display:block;font-size:.86rem;color:var(--ink-3);margin-top:.2rem}
.cover-foot{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:center;
  gap:.45rem .9rem;border-top:1px solid var(--line);padding-top:1.1rem}
.book-author{font-family:var(--sans);letter-spacing:.28em;text-indent:.28em;
  color:var(--ink);font-size:.95rem;font-weight:700}
.cover-ver{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;
  color:var(--ink-3)}
.cover-ver b{color:var(--cinnabar);font-weight:700}
.cover-tag{font-family:var(--sans);font-size:.74rem;letter-spacing:.36em;
  color:var(--bronze);text-transform:uppercase;margin:0 0 2.2rem}
.imprint-list{margin:0 0 1.6rem}
.ip-row{display:grid;grid-template-columns:8.5rem 1fr;gap:1rem;padding:.55rem 0;
  border-bottom:1px solid var(--line);align-items:baseline}
.ip-row dt{font-family:var(--sans);font-size:.8rem;letter-spacing:.2em;
  color:var(--bronze);margin:0}
.ip-row dd{margin:0}
@media (max-width:30rem){
  .ip-row{grid-template-columns:1fr;gap:.18rem}
}
.ip-notice-t{margin:1.4rem 0 .4rem;font-size:.95rem;color:var(--cinnabar)}
.ip-notice{color:var(--ink-2);font-size:.95rem;border-left:3px solid var(--line-2);
  padding-left:1rem}
.rev-v{display:flex;justify-content:space-between;align-items:baseline;
  font-size:1.05rem;margin:1.35rem 0 .4rem;padding-bottom:.25rem;
  border-bottom:1px solid var(--line);color:var(--bronze-3)}
.rev-v .rev-d{font-size:.78rem;color:var(--ink-3);font-weight:400;
  font-variant-numeric:tabular-nums}
.revisions ul{margin:.3rem 0 .2rem;padding-left:1.4rem;font-size:.95rem;
  line-height:1.78;color:var(--ink-2);list-style-type:none}
/* the diamond is the only bullet, scoped strictly to prose and revision lists
   so structural component lists (routes, index, sources, principles, terms,
   route map) never wear a floating diamond in their negative margin */
ul{list-style:none}
.chapter-body ul:not([class])>li,.revisions ul>li{position:relative}
.chapter-body ul:not([class])>li::before,.revisions ul>li::before{content:"◆";
  position:absolute;left:-1.15em;top:0;font-size:.55em;
  color:var(--bronze-2);line-height:2.8}
.revisions li::marker{color:var(--bronze-2)}
/* four routes, one row: at 15rem the sheet broke 3+1 and the orphan card left
   two empty cells the reader scans as missing content */
.route-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(12.5rem,1fr));
  gap:.9rem;margin:1.1rem 0 1.6rem}
/* four routes never divide into a three-up row. Rather than leave the last
   row two-thirds empty, the fourth card takes the whole line and reads as the
   closing note it is */
.route-grid>:last-child:nth-child(4){grid-column:1/-1}
.route-card{background:var(--card);border:1px solid var(--line);border-radius:var(--r-2);
  padding:1.05rem 1.2rem;border-top:2.5px solid var(--bronze-2);
  box-shadow:0 2px 8px -4px rgba(38,34,27,.10);
  transition:transform .16s ease,box-shadow .16s ease,border-top-color .16s ease}
.route-card:hover{border-top-color:var(--cinnabar);
  box-shadow:0 8px 18px -10px rgba(38,34,27,.22)}
.route-card h3{margin:0 0 .35rem;font-size:.92rem;color:var(--cinnabar);
  letter-spacing:.05em}
.route-card p{margin:0;font-size:.95rem;color:var(--ink-2)}
@media (prefers-color-scheme:dark){
  body:not(.force-light) .route-card{box-shadow:0 4px 14px -8px rgba(0,0,0,.55)}
}
/* the route map is its own leaf, not furniture on the reading-paths sheet:
   that page already carries the routes, the offline note, the parts list and
   the legend, and print has no room to spare for a second block that must not
   split. Here the map is the page, so it gets `break-inside:avoid` outright. */
.itinerary{display:block;width:min(46rem,100%);height:auto;break-inside:avoid;
  margin:.2rem auto 1.1rem;color:var(--bronze);opacity:.92}
.itinerary text{font-family:var(--sans);font-size:11px;fill:currentColor;
  stroke:none;letter-spacing:.02em}
.rm-lead{max-width:36rem;margin:.45rem auto 1.35rem;text-align:center;
  color:var(--ink-2);font-size:1.02rem}
/* the legend is read once and never looked at again, so it stays small, in the
   sans, and directly under the map it explains */
.rm-key{display:flex;flex-wrap:wrap;justify-content:center;gap:.35rem 1.5rem;
  list-style:none;margin:0 auto 1.6rem;padding:0;max-width:44rem;
  font-family:var(--sans);font-size:.76rem;letter-spacing:.02em;color:var(--ink-3)}
.rm-key li{display:flex;align-items:center;gap:.42rem}
.rmk{flex:none;width:1.05rem;height:1.05rem;color:var(--bronze)}
.rm-legs{list-style:none;margin:0 auto;padding:.85rem 0 0;max-width:34rem;
  border-top:1px solid var(--line)}
.rm-legs li{display:flex;flex-direction:column;gap:.15rem;padding:.42rem 0;
  border-bottom:1px solid var(--line);line-height:1.62}
.rm-legs li:last-child{border-bottom:0}
/* the two lines of a row are furniture text, not prose: the browser's own
   paragraph margins would otherwise spend more sheet than the sentences do */
.rm-legs p{margin:0}
.rm-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:.15rem .6rem}
.rm-head a{font-family:var(--sans);font-weight:700;color:var(--bronze-3)}
.rm-nos{font-family:var(--sans);font-size:.8rem;color:var(--cinnabar);
  letter-spacing:.08em}
.rm-why{color:var(--ink-2);font-size:.92rem}
.route-parts{list-style:none;margin:0;padding:0}
.route-parts li{padding:.55rem 0;border-bottom:1px solid var(--line);
  display:flex;flex-direction:column;gap:.15rem}
.route-parts a{font-family:var(--sans);font-weight:700;color:var(--bronze-3);
  text-decoration:none}
.route-goal{font-size:.9rem;color:var(--ink-3)}

/* ------- TOC ------- */
.toc-part{display:flex;align-items:baseline;gap:.85rem;margin:1.6rem 0 .5rem;
  font-family:var(--sans);font-weight:700;font-size:.85rem;letter-spacing:.2em;
  color:var(--bronze);text-decoration:none}
.toc-part:hover .tp-tx,.toc-part:hover .tp-no{color:var(--cinnabar)}
.toc-part::after{content:"";flex:1;height:1px;background:var(--line-2);
  transform:translateY(-.32em);order:2}
.toc-part .page-ref{order:3}
/* the numeral is inked, not outlined: a hollow 1.9rem Ⅰ is the loudest mark on
   the contents page and, being empty inside, reads as a plate that failed to
   take ink */
.tp-no{font-family:var(--serif);font-size:1.15rem;font-weight:700;
  line-height:1;color:var(--bronze);letter-spacing:.06em}
.tp-tx{color:var(--bronze-3)}
.toc-part-plain{color:var(--cinnabar);margin-top:2.4rem}
.toc-hr{border:none;border-top:1px solid var(--line);margin:1.2rem 0}
.toc-group{break-inside:avoid}
/* a bound volume outranks a part: in the omnibus each volume restarts its
   own Ⅰ–Ⅶ, so the volume row needs its own rank and its own air */
.toc-vol{display:flex;align-items:baseline;gap:.85rem;margin:2.5rem 0 .55rem;
  padding-top:1.05rem;border-top:2px solid var(--line-2);
  font-family:var(--sans);font-weight:700;font-size:.95rem;letter-spacing:.24em;
  color:var(--bronze);text-decoration:none}
.toc-vol .tp-no{font-size:1.5rem;color:var(--cinnabar)}
.toc-vol .tp-tx{color:var(--ink)}
.toc-vol::after{content:"";flex:1;height:1px;background:var(--line-2);
  transform:translateY(-.32em);order:2}
.toc-vol .page-ref{order:3}
.toc-vol:hover .tp-tx,.toc-vol:hover .tp-no{color:var(--cinnabar)}
.vol-tag{font-family:var(--sans);font-weight:700;color:var(--cinnabar);
  letter-spacing:.12em;flex:0 0 auto}
.vol-tag::after{content:"·";margin-left:.7rem;color:var(--bronze-2)}
.toc-row{display:flex;align-items:baseline;text-decoration:none;color:var(--ink);
  padding:.32rem .35rem .3rem;margin:0 -.35rem;font-size:.99rem;border-radius:var(--r-1);
  transition:transform .16s ease,color .16s ease,background-color .16s ease}
.toc-row:hover{color:var(--cinnabar);background:rgba(243,234,216,.42)}
.toc-row:hover .toc-n{color:var(--cinnabar);border-color:var(--cinnabar)}
.toc-row:focus-visible{outline:2px solid var(--cinnabar);outline-offset:1px}
@media (prefers-color-scheme:dark){
  body:not(.force-light) .toc-row:hover{background:rgba(34,34,28,.65)}}
.toc-n{flex:0 0 auto;min-width:2.1rem;margin-inline-end:.75rem;text-align:center;
  font-family:var(--sans);font-size:.7rem;font-weight:700;color:var(--bronze-3);
  border:1px solid var(--line-2);border-radius:var(--r-1);padding:.1rem .2rem;
  transform:translateY(-.12em)}
.toc-n-guide{color:var(--cinnabar);border-color:var(--cinnabar);background:var(--paper-2)}
.toc-t{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:30rem){
  .toc-t{white-space:normal;overflow:visible;text-overflow:clip;line-height:1.45}
  .toc-row .leader{display:none}
}
/* the leader carries the eye from a title to its folio, so it is drawn in the
   ornament gold rather than in the rule grey it kept getting lost in */
.leader{flex:1;border-bottom:1px dotted var(--bronze-2);margin:0 .5rem;
  transform:translateY(-.28em)}
.page-ref{font-family:var(--sans);font-size:.86rem;color:var(--bronze-3);
  font-variant-numeric:tabular-nums;min-width:1.6rem;
  text-align:right}

/* ------- part dividers ------- */
.part-divider{position:relative;overflow:hidden;text-align:center;
  padding:clamp(2.4rem,6vw,4rem) 1rem clamp(2rem,5vw,3.2rem);
  break-before:page;break-after:page;
  background:
    radial-gradient(120% 90% at 50% 0%,var(--paper-2) 0%,transparent 62%),
    linear-gradient(180deg,transparent,rgba(200,164,92,.06))}
@media (prefers-color-scheme:dark){
  body:not(.force-light) .part-divider{
    background:
      radial-gradient(120% 90% at 50% 0%,var(--paper-2) 0%,transparent 62%),
      linear-gradient(180deg,transparent,rgba(224,123,95,.035))}
}
.part-divider::before,.part-divider::after{content:"";position:absolute;
  left:50%;transform:translateX(-50%);width:min(70%,44rem);
  border-top:1px solid var(--line-2)}
.part-divider::before{top:1.4rem}
.part-divider::after{bottom:1.4rem}
/* the ghost wheel bleeds off one corner instead of sitting behind the plate:
   concentric wheels would double the rim, an off-centre arc gives the page a
   second, larger drawing to rest against */
.pd-ghost{position:absolute;right:-14%;top:-9%;width:min(360px,58vw);
  color:var(--bronze-2);opacity:.11;pointer-events:none;user-select:none}
.pd-ghost svg{width:100%;height:auto;display:block}
.pd-inner{position:relative;max-width:38rem;margin:0 auto;padding-top:clamp(3.4rem,8vw,5rem)}
/* the part's own drawing sits over the faint wheel: crisp line on ghosted
   line, the same depth the cover plate gets. Everything here is inked in
   currentColor, so dark mode and paper re-ink the drawing on their own. */
.pd-art{width:min(13.5rem,62%);margin:0 auto 1.1rem;color:var(--bronze);opacity:.9}
.pd-art svg{width:100%;height:auto;display:block}
.pd-art img{width:100%;height:auto;display:block}
.pd-no{font-family:var(--sans);letter-spacing:.5em;text-indent:.5em;
  color:var(--bronze);font-size:.85rem;margin:0 0 .5rem}
.pd-title{font-size:clamp(2rem,5.5vw,2.7rem);margin:0;letter-spacing:.08em}
.pd-count{font-family:var(--sans);font-size:.74rem;letter-spacing:.18em;
  color:var(--bronze);margin:.55rem 0 0;font-variant-numeric:tabular-nums}
/* a volume door is the outer binding; it must not read as the first part of
   the volume it opens. The larger numeral and tighter rule give it one rank
   above the part sheets that follow. */
.collected .volume-divider{padding-top:clamp(2.8rem,7vw,4.6rem)}
.collected .volume-divider .pd-no{font-size:1rem;color:var(--cinnabar);
  letter-spacing:.62em}
.collected .volume-divider .pd-title{letter-spacing:.12em}
.collected .volume-divider .cover-rule{margin-top:1.15rem}
.collected .volume-divider .pd-count{display:inline-block;padding:.14rem .75rem;
  border:1px solid var(--line-2);border-radius:var(--r-1);background:var(--card);
  margin-top:.75rem}
#collection-guide .chapter-body>p:first-of-type::first-letter{
  font-size:inherit;line-height:inherit;float:none;padding:0;
  color:inherit;font-weight:inherit;font-family:inherit}
.pd-motto{font-family:var(--kai);color:var(--cinnabar);margin:.2rem 0 1.3rem;
  letter-spacing:.14em;font-size:1.02rem}
.pd-goal{max-width:30rem;margin:0 auto;color:var(--ink-2);font-size:.98rem;
  line-height:1.9;text-wrap:balance}
/* the leg's road, drawn once above the stop list: the reader sees how many
   chapters the part is before reading a single one of their titles */
.pd-route{display:block;width:min(23rem,92%);height:auto;margin:1.55rem auto .1rem;
  color:var(--bronze);opacity:.85}
.pd-list{list-style:none;margin:1.1rem auto 0;padding:.9rem 0 0;max-width:26rem;
  text-align:start;border-top:1px solid var(--line-2)}
.pd-list.pd-list-cols{max-width:38rem;display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));column-gap:1.8rem}
@media (max-width:38rem){.pd-list.pd-list-cols{grid-template-columns:1fr}}
.pd-list li{padding:.42rem 0;border-bottom:1px solid var(--line)}
.pd-list a{text-decoration:none;color:var(--ink-2);font-size:.95rem;
  display:flex;gap:.7rem;align-items:baseline}
.pd-list a:hover{color:var(--cinnabar)}
.pd-list a::before{content:attr(data-no);
  font-family:var(--sans);font-size:.74rem;color:var(--bronze);
  font-variant-numeric:tabular-nums;flex:0 0 auto}

/* anchor landing spotlight: jumping from TOC, cross-reference, or footnote
   gives the landed section or citation row a quiet visual cue without JS */
article.chapter :is(h2,h3,h4):target,
.reg-list li:target,
.notes-list li:target{scroll-margin-top:4rem}
.reg-list li:target{border-inline-start-color:var(--cinnabar);
  background:var(--paper-2)}
.notes-list li:target{background:var(--paper-2);border-radius:var(--r-1);
  padding-inline:.45rem}
article.chapter :is(h2,h3,h4):target{color:var(--cinnabar)}
/* ------- chapters ------- */
article.chapter,article.unit{padding:1.7rem 0 2.2rem;break-before:page;
  overflow-wrap:break-word}
.chapter-head .eyebrow{font-family:var(--sans);font-size:.78rem;
  letter-spacing:.3em;color:var(--bronze);text-transform:uppercase;
  margin:0 0 .3rem;display:flex;align-items:center;gap:.7rem}
.chapter-head .eyebrow::after{content:"";flex:1;height:1px;
  background:linear-gradient(90deg,var(--line-2),transparent)}
article h1{font-size:1.85rem;margin:.15rem 0 1.05rem;line-height:1.4}
.ch-head-row{display:flex;align-items:flex-start;gap:1.05rem}
.ch-seal{flex:0 0 auto;display:grid;place-items:center;width:3.05rem;height:3.05rem;
  margin-top:.25rem;border:2px solid var(--cinnabar);border-radius:var(--r-1);
  color:var(--cinnabar);background:var(--card);
  transform:rotate(-1.7deg);
  font-family:Georgia,var(--sans);font-weight:700;font-size:1.32rem;
  letter-spacing:.02em;font-variant-numeric:tabular-nums;
  box-shadow:inset 0 0 0 1px rgba(180,71,47,.16),0 3px 10px -6px rgba(180,71,47,.28)}
.ch-head-row h1{margin-bottom:1.05rem;min-width:0}
.appendix .ch-seal{border-color:var(--cinnabar);color:var(--cinnabar)}
@media (prefers-color-scheme:dark){
  body:not(.force-light) .ch-seal{box-shadow:inset 0 0 0 1px rgba(224,123,95,.24),0 3px 10px -6px rgba(0,0,0,.5)}
}
/* the unit emblem: drawn with currentColor so it re-inks itself in dark mode
   and on paper, and floats into the head row rather than eating a block of
   vertical space the way a full-width figure would */
.ch-emblem{flex:0 0 auto;align-self:center;margin-inline-start:auto;
  width:4.6rem;height:4.6rem;color:var(--bronze);opacity:.92}
.ch-emblem svg{width:100%;height:100%;display:block}
.appendix .ch-emblem{color:var(--cinnabar);opacity:.8}
/* a generated plate is black ink on a transparent field, so dark mode flips it
   the way a currentColor drawing re-inks itself; paper and print stay black */
@media screen and (prefers-color-scheme:dark){
  body:not(.force-light) .ink-plate{filter:invert(1)}}
@media (max-width:44rem){.ch-emblem{width:3.2rem;height:3.2rem}}
/* the ink draws itself as a unit scrolls into view. Triple-guarded so the
   drawing can never half-exist where motion cannot run: print/PDF (screen
   only), reduced-motion readers, and browsers without scroll-driven
   animations all fall through to the fully inked static drawing. The
   animation targets only shapes carrying pathLength="100" — dashed strokes
   keep their real-unit dash rhythm and fade instead, and ink dots pop. */
@media screen and (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    /* :not([stroke-dasharray]) matters: an authored dash rhythm is a real
       drawing decision, and `stroke-dasharray:100 100` below would overwrite
       it on every dashed path that also carries pathLength. Those shapes get
       ink-fade from the rule that follows instead, as intended. */
    .ch-emblem path[pathLength]:not([stroke-dasharray]),.ch-emblem circle[pathLength]:not([stroke-dasharray]),
    .kp-art path[pathLength]:not([stroke-dasharray]),.kp-art circle[pathLength]:not([stroke-dasharray]),
    .pd-art path[pathLength]:not([stroke-dasharray]),.pd-art circle[pathLength]:not([stroke-dasharray]),
    .cover-art path[pathLength]:not([stroke-dasharray]),.cover-art circle[pathLength]:not([stroke-dasharray]),
    .ch-trace path[pathLength]:not([stroke-dasharray]),.ch-trace circle[pathLength]:not([stroke-dasharray]),
    .pd-route path[pathLength]:not([stroke-dasharray]),.pd-route circle[pathLength]:not([stroke-dasharray]),
    .illu-frame path[pathLength]:not([stroke-dasharray]),.illu-frame circle[pathLength]:not([stroke-dasharray]),
    .itinerary path[pathLength]:not([stroke-dasharray]),.itinerary circle[pathLength]:not([stroke-dasharray]){
      stroke-dasharray:100 100;
      animation:ink-draw 1.2s ease-out both;
      animation-timeline:view();
      animation-range:cover 0% cover 60%}
    .ch-emblem [stroke-dasharray],.kp-art [stroke-dasharray],
    .pd-art [stroke-dasharray],.cover-art [stroke-dasharray],
    .illu-frame [stroke-dasharray],
    .itinerary [stroke-dasharray]{
      animation:ink-fade 1s ease-out both;
      animation-timeline:view();
      animation-range:cover 0% cover 55%}
    .ch-emblem [fill="currentColor"],.kp-art [fill="currentColor"],
    .pd-art [fill="currentColor"],.cover-art [fill="currentColor"],
    .ch-trace [fill="currentColor"],.pd-route [fill="currentColor"],
    .illu-frame [fill="currentColor"],
    .itinerary [fill="currentColor"]{
      transform-box:fill-box;transform-origin:center;
      animation:ink-pop .7s cubic-bezier(.2,1.4,.4,1) both;
      animation-timeline:view();
      animation-range:cover 8% cover 62%}
    .ch-rut,.hr-knot,.ink-mark,.rmk{
      animation:ink-fade 1s ease-out both;
      animation-timeline:view();
      animation-range:cover 0% cover 55%}
    /* a sequential plate carries its story in frames. Each group fades in on
       its own slice of the scroll, so the mechanism visibly moves instead of
       arriving as one frozen last frame; the strokes inside still ink
       themselves. Print and reduced-motion lose the stagger and keep every
       frame drawn — the strip still reads in order, which is the point. */
    .illu-seq .frame{animation:ink-fade 1s ease-out both;
      animation-timeline:view()}
    .illu-seq .frame:nth-child(1){animation-range:cover 0% cover 26%}
    .illu-seq .frame:nth-child(2){animation-range:cover 10% cover 40%}
    .illu-seq .frame:nth-child(3){animation-range:cover 22% cover 54%}
    .illu-seq .frame:nth-child(4){animation-range:cover 34% cover 68%}
    .illu-seq .frame:nth-child(5){animation-range:cover 46% cover 80%}
    .illu-seq .frame:nth-child(6){animation-range:cover 58% cover 92%}
    /* hovering runs the strip: one frame lit at a time, walking left to right.
       The scroll range is dropped for a plain clock, and the strokes stay
       inked, so only the light moves. */
    .illu-seq:hover .frame{animation:ink-cycle 2.8s linear infinite both;
      animation-timeline:auto;animation-range:normal}
    .illu-seq:hover .frame:nth-child(2){animation-delay:.7s}
    .illu-seq:hover .frame:nth-child(3){animation-delay:1.4s}
    .illu-seq:hover .frame:nth-child(4){animation-delay:2.1s}
    .illu-seq:hover .frame:nth-child(5){animation-delay:2.8s}
    .illu-seq:hover .frame:nth-child(6){animation-delay:3.5s}
    /* character: hovering wakes a drawing up. Spring easings, squash and
       stretch — the twelve-principles vocabulary in three-line keyframes.
       Each figure carries its pivot in a class, so one verb per drawing. */
    .a-compass:hover .spin{animation:ink-spin-c 26s linear infinite}
    .a-chase .spin{transform-box:view-box;transform-origin:32px 32px}
    .a-chase:hover .spin{animation:ink-spin 7s linear infinite}
    .a-nut .wiggle{transform-box:view-box;transform-origin:32px 32px}
    .a-nut:hover .wiggle{animation:ink-wiggle 1s cubic-bezier(.36,.07,.19,.97) infinite alternate}
    .a-gauge .sweep{transform-box:view-box;transform-origin:32px 44px}
    .a-gauge:hover .sweep{animation:ink-sweep 1.5s ease-in-out infinite alternate}
    .a-hook .nudge{transform-box:fill-box;transform-origin:center}
    .a-hook:hover .nudge{animation:ink-nudge .7s cubic-bezier(.36,.07,.19,.97) infinite alternate}
    .a-hub .pulse{transform-box:fill-box;transform-origin:center}
    .a-hub:hover .pulse{animation:ink-pulse 1.1s cubic-bezier(.34,1.56,.64,1) infinite}
    .a-wire .sway{transform-box:view-box;transform-origin:32px 14px}
    .a-wire:hover .sway{animation:ink-sway 1.7s ease-in-out infinite alternate}
    .a-funnel .drip{transform-box:fill-box;transform-origin:center}
    .a-funnel:hover .drip{animation:ink-drip 1s cubic-bezier(.55,0,1,.45) infinite}
    .a-flag .wave{transform-box:view-box;transform-origin:47px 12px}
    .a-flag:hover .wave{animation:ink-wave 1.3s ease-in-out infinite alternate}
    .a-toggle .knob{transform-box:fill-box;transform-origin:center}
    .a-toggle:hover .knob{animation:ink-toggle 1s cubic-bezier(.34,1.56,.64,1) infinite alternate}
    .a-keeper .swing{transform-box:view-box;transform-origin:45.2px 39.3px}
    /* row-level trigger: the hop moves the drawing itself, so hovering the
       small svg directly would push it out from under the cursor and flicker */
    .keeper:hover .a-keeper .swing,.keeper:focus-within .a-keeper .swing{
      animation:ink-swing 1.5s ease-in-out infinite alternate}
    .keeper:hover .a-keeper,.keeper:focus-within .a-keeper{
      animation:ink-hop .9s cubic-bezier(.36,.07,.19,.97) infinite alternate}
    /* the chariot rides as the reader does: wheels roll, the team bobs */
    .cover-art .roll{transform-box:view-box;transform-origin:668px 336px;
      animation:ink-roll 1.1s linear both;animation-timeline:view();
      animation-range:cover 0% cover 85%}
    .cover-art .bob{animation:ink-bob 1.3s ease-in-out both;
      animation-timeline:view();animation-range:cover 0% cover 70%}
    .pd-art .turn{transform-box:view-box;transform-origin:100px 64px;
      animation:ink-turn 1.2s ease-out both;animation-timeline:view();
      animation-range:cover 0% cover 70%}
    /* and the roads walk: a dashed route marches one period at a time, so
       the 驿路 itself travels under the reader's eye */
    .a-front:hover .m75{animation:ink-march-75 1s linear infinite}
    .a-flag:hover .m92{animation:ink-march-92 1.1s linear infinite}
    .a-path:hover .m80{animation:ink-march-80 1.05s linear infinite}
    .itinerary .m110{animation:ink-march-110 1.3s linear infinite}
    .a-gate:hover .redraw{animation:ink-redraw 1.1s ease-out infinite}
    .a-memo:hover .write{animation:ink-redraw 1.3s ease-out infinite}
    .a-list:hover .tick{animation:ink-redraw .8s ease-out infinite}
    .a-list:hover .t2{animation-delay:.15s}
    .a-list:hover .t3{animation-delay:.3s}
    .a-stack .ripple{transform-box:fill-box;transform-origin:center}
    .a-stack:hover .d1{animation:ink-ripple .9s ease-out infinite}
    .a-stack:hover .d2{animation:ink-ripple .9s ease-out .15s infinite}
    .a-fork .pulse,.a-locate .pulse{transform-box:fill-box;transform-origin:center}
    .a-fork:hover .pulse{animation:ink-pulse 1s cubic-bezier(.34,1.56,.64,1) infinite}
    .a-locate:hover .pulse{animation:ink-pulse 1.2s cubic-bezier(.34,1.56,.64,1) infinite}
    .a-plug:hover .blink{animation:ink-blink 1.1s linear infinite}
    .a-plug:hover .b2{animation-delay:.55s}
    .a-gloss .flutter{transform-box:fill-box;transform-origin:50% 0%}
    .a-gloss:hover .f1{animation:ink-flutter .8s ease-in-out infinite alternate}
    .a-gloss:hover .f2{animation:ink-flutter .8s ease-in-out .2s infinite alternate}
    /* text rises the way the drawings land: headings, callouts and cards
       settle onto the sheet as the reader reaches them */
    .ch-head-row h1,.h1-sub,.page-title,
    .chapter-body h2,.chapter-body h3,
    .callout,.lead-band,.compass-card,.route-card,.keeper-note,.new-terms,
    .pd-title,.pd-motto,.pd-goal,.rm-head,.pd-list li,
    .diagram-frame,.fig-cap,figure.illu figcaption{
      animation:ink-rise .9s cubic-bezier(.22,.9,.3,1) both;
      animation-timeline:view();
      animation-range:cover 0% cover 42%}
    /* the ghost wheel behind a part divider slowly turns as the reader rides */
    .pd-ghost svg{transform-box:view-box;transform-origin:100px 100px;
      animation:ink-ghost 1.6s ease-out both;animation-timeline:view();
      animation-range:cover 0% cover 80%}
    /* pure-CSS reading progress thread along the top edge: zero JS,
       GPU-composited transform, gated behind screen + motion + scroll timeline */
    body::before{content:"";position:fixed;inset:0 0 auto 0;height:2.5px;
      z-index:60;pointer-events:none;transform-origin:0 50%;
      background:linear-gradient(90deg,var(--cinnabar),var(--bronze-2));
      animation:yuyu-progress linear both;
      animation-timeline:scroll(root block)}
  }
  /* load- and hover-driven text motion needs no scroll timeline, only the
     reduced-motion hand */
  .front-page.cover .cover-kicker{animation:ink-rise .7s ease-out both}
  .front-page.cover .book-title{animation:ink-rise .8s ease-out .12s both}
  .front-page.cover .book-sub{animation:ink-rise .8s ease-out .24s both}
  .front-page.cover .book-epi{animation:ink-rise .8s ease-out .36s both}
  .front-page.cover .cover-foot{animation:ink-rise .8s ease-out .48s both}
  .gloss:hover .gloss-pop,.gloss:focus .gloss-pop,
  .gloss:focus-within .gloss-pop{
    animation:ink-gloss .32s cubic-bezier(.34,1.56,.64,1)}
  .source-chip,.tier-chip{transition:transform .16s ease,box-shadow .16s ease}
  .source-chip:hover,.tier-chip:hover{transform:translateY(-1.5px);
    box-shadow:0 3px 8px rgba(38,34,27,.14)}
  .toc-row{transition:transform .18s ease}
  .toc-row:hover{transform:translateX(3px)}
  .route-card:hover{transform:translateY(-2px)}
  /* the compass ring keeps its hand-set phase even where motion is off */
  .a-compass .spin{transform:rotate(9deg);transform-box:view-box;
    transform-origin:32px 32px}
}
@keyframes ink-draw{from{stroke-dashoffset:100}}
@keyframes ink-fade{from{opacity:0}}
@keyframes ink-cycle{0%,100%{opacity:.26}12%,30%{opacity:1}}
@keyframes ink-pop{0%{transform:scale(0)}60%{transform:scale(1.25,.75)}
  80%{transform:scale(.92,1.12)}100%{transform:scale(1)}}
@keyframes ink-spin{to{transform:rotate(360deg)}}
@keyframes ink-spin-c{from{transform:rotate(9deg)}to{transform:rotate(369deg)}}
@keyframes ink-wiggle{from{transform:rotate(-7deg)}to{transform:rotate(7deg)}}
@keyframes ink-sweep{from{transform:rotate(-12deg)}to{transform:rotate(14deg)}}
@keyframes ink-nudge{from{transform:translateX(0)}to{transform:translateX(3px)}}
@keyframes ink-pulse{0%{transform:scale(1)}45%{transform:scale(1.3)}100%{transform:scale(1)}}
@keyframes ink-sway{from{transform:rotate(-1.4deg)}to{transform:rotate(1.4deg)}}
@keyframes ink-drip{0%{transform:translateY(0);opacity:.55}
  70%{opacity:.55}100%{transform:translateY(6px);opacity:0}}
@keyframes ink-wave{from{transform:rotate(-4deg)}to{transform:rotate(5deg)}}
@keyframes ink-toggle{0%{transform:translateX(0)}55%{transform:translateX(-25px)}
  75%{transform:translateX(-19px)}100%{transform:translateX(-21px)}}
@keyframes ink-swing{from{transform:rotate(-10deg)}to{transform:rotate(10deg)}}
@keyframes ink-hop{from{transform:translateY(0)}to{transform:translateY(-2px)}}
@keyframes ink-roll{to{transform:rotate(-160deg)}}
@keyframes ink-bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
@keyframes ink-turn{to{transform:rotate(45deg)}}
@keyframes ink-march-75{to{stroke-dashoffset:-7.5}}
@keyframes ink-march-92{to{stroke-dashoffset:-9.2}}
@keyframes ink-march-80{to{stroke-dashoffset:-8}}
@keyframes ink-march-110{to{stroke-dashoffset:-11}}
@keyframes ink-redraw{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
@keyframes ink-ripple{0%{transform:translateY(0)}
  55%{transform:translateY(2.5px)}100%{transform:translateY(0)}}
@keyframes ink-blink{0%,45%{opacity:1}50%,95%{opacity:.12}100%{opacity:1}}
@keyframes ink-flutter{from{transform:rotate(-5deg)}to{transform:rotate(6deg)}}
@keyframes ink-rise{from{opacity:0;transform:translateY(12px)}}
@keyframes ink-gloss{from{opacity:0;transform:translate(-50%,.5rem) scale(.9)}
  to{opacity:1;transform:translate(-50%,0) scale(1)}}
@keyframes ink-ghost{to{transform:rotate(26deg)}}
@keyframes yuyu-progress{from{transform:scaleX(0)}to{transform:scaleX(1)}}
/* the wire the head closes on — a drawn line with pads, not a ruled one.
   Inline SVG, so it inherits currentColor like every other drawing here. */
.ch-trace{display:block;width:min(21rem,100%);height:auto;
  margin:-.15rem 0 .35rem;color:var(--bronze-2);opacity:.75}
.appendix .ch-trace{color:var(--cinnabar);opacity:.5}
/* and the ruts it ends on: a drawn full stop for the chapter, so the tail of
   the page closes on something the book inked rather than on blank paper */
.ch-rut{display:block;width:min(17rem,74%);height:auto;break-before:avoid;
  margin:2.1rem auto .15rem;color:var(--bronze);opacity:.8}
.appendix .ch-rut{color:var(--cinnabar);opacity:.62}
article h1 .h1-sub{display:block;font-weight:400;font-size:1.05rem;
  color:var(--ink-3);margin-top:.35rem;font-family:var(--serif)}
article h2{font-size:1.28rem;margin:2.15rem 0 .8rem;padding:0 0 .34rem .78rem;
  border-left:3.5px solid var(--cinnabar);border-bottom:1px solid var(--line)}
article h3{font-size:1.06rem;margin:1.55rem 0 .5rem;color:var(--bronze-3);
  letter-spacing:.015em}
article h4{font-size:.95rem;margin:1.15rem 0 .38rem;color:var(--ink-2)}
article h2 .sec-no{color:var(--bronze);margin-right:.45rem;font-variant-numeric:tabular-nums}
article p{margin:0 0 1.08em}
article strong{color:var(--ink);font-weight:700}
article em{font-family:var(--kai);font-style:normal;color:var(--bronze-3)}
body.lang-en article em{font-family:inherit;font-style:italic;color:inherit}
article .chapter-body>p:first-of-type::first-letter{
  font-size:2.95em;line-height:.84;float:inline-start;
  padding:.09em .14em 0 0;color:var(--cinnabar);font-weight:700;
  font-family:"STSong","Songti SC","Noto Serif SC",var(--serif)}
/* Chinese has no one-letter words: a display initial splits the first term
   ("周/六上午", "任/务卡"), so the field guide opens on the sentence instead. */
.vibe article .chapter-body>p:first-of-type::first-letter{
  font-size:inherit;line-height:inherit;float:none;padding:0;
  color:inherit;font-weight:inherit;font-family:inherit}
ul,ol{padding-inline-start:1.6em;margin:0 0 1.08em}
li{margin:.28em 0}
li::marker{color:var(--bronze);font-family:var(--sans);font-size:.88em;
  font-weight:600;font-variant-numeric:tabular-nums}
hr{border:none;text-align:center;margin:1.8rem 0}
/* the section break: hairline, drawn coupling, hairline. The coupling is an
   inline SVG rather than a typed glyph, so it re-inks in dark mode and on
   paper exactly like the emblems do. */
.hr-rule{display:flex;align-items:center;gap:.8rem;margin:1.7rem 0 1.8rem;
  color:var(--bronze-2)}
.hr-rule::before,.hr-rule::after{content:"";flex:1;height:1px;
  background:var(--line-2)}
/* plain 1px lines, not gradients: a gradient background is painted as a raster
   image by the print engine, and this rule appears 111 times per edition */
.hr-knot{flex:0 0 auto;width:3.4rem;height:auto}
/* mermaid ships its own <style> inside each diagram, edge-dash loops included;
   a reader who asked for reduced motion gets the finished drawing */
@media (prefers-reduced-motion: reduce){svg *{animation:none!important}}

"""
