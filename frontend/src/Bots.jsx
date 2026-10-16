import React from 'react';
export const ROLES=['manager','research','strategy','writing','creative','brand_review','publishing','analytics','optimization','engagement'];
export const BOTS={
 manager:{name:'Marketing Manager',job:'Coordinates your team',color:'#bce992',glyph:'star'},
 research:{name:'Research Bot',job:'Checks facts and context',color:'#73ccdf',glyph:'search'},
 strategy:{name:'Strategy Bot',job:'Builds the campaign plan',color:'#a5a3f6',glyph:'compass'},
 writing:{name:'Writer Bot',job:'Writes your content',color:'#f3bd78',glyph:'pen'},
 creative:{name:'Creative Bot',job:'Builds the visual direction',color:'#e5a6f0',glyph:'palette'},
 brand_review:{name:'Brand Guardian',job:'Checks facts and brand rules',color:'#7cd5b5',glyph:'shield'},
 publishing:{name:'Publisher Bot',job:'Publishes the approved version',color:'#8eb9f1',glyph:'send'},
 analytics:{name:'Analytics Bot',job:'Measures and explains results',color:'#a9d281',glyph:'chart'},
 optimization:{name:'Optimizer Bot',job:'Proposes the next experiment',color:'#f1d279',glyph:'bolt'},
 engagement:{name:'Community Bot',job:'Prepares audience replies',color:'#f1a3b5',glyph:'chat'},
 'local-owner':{name:'You',job:'Workflow owner',color:'#c3c8d2',glyph:'person'},
 controller:{name:'Marketing Manager',job:'Coordinates your team',color:'#bce992',glyph:'star'}
};
export function Icon({name,size=18}){const p={
 star:<path d="m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9Z"/>,
 search:<><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></>,
 compass:<><circle cx="12" cy="12" r="9"/><path d="m16 8-3 5-5 3 3-5Z"/></>,
 pen:<><path d="m4 16 12-12 4 4-12 12-5 1Z"/><path d="m13 7 4 4"/></>,
 palette:<><path d="M12 3a9 9 0 1 0 0 18h2a3 3 0 0 0 1-6c-2-1 0-2 2-2h1a3 3 0 0 0 3-3c0-4-4-7-9-7Z"/><circle cx="8" cy="9" r=".7"/><circle cx="12" cy="6" r=".7"/><circle cx="16" cy="8" r=".7"/></>,
 shield:<><path d="m12 3 8 3v6c0 5-8 9-8 9S4 17 4 12V6Z"/><path d="m8 12 3 3 5-6"/></>,
 send:<><path d="m3 4 18 8-18 8 3-8Z"/><path d="M6 12h15"/></>,
 chart:<><path d="M4 3v17h17M8 16v-4m5 4V7m5 9v-6"/></>,
 bolt:<path d="m14 2-9 12h6l-1 8 9-12h-6Z"/>,
 chat:<path d="M4 4h16v12H9l-5 4Z"/>,
 person:<><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></>,
 grid:<><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
 plus:<path d="M12 4v16M4 12h16"/>,
 settings:<><path d="M3 7h18M3 17h18"/><circle cx="9" cy="7" r="3"/><circle cx="16" cy="17" r="3"/></>,
 check:<path d="m5 12 4 4 10-10"/>,
 arrow:<path d="M4 12h16m-5-5 5 5-5 5"/>,
 bell:<><path d="M6 9a6 6 0 0 1 12 0v7l3 2H3l3-2ZM10 21h4"/></>,
 close:<path d="m6 6 12 12M6 18 18 6"/>,
 play:<path d="m8 4 12 8-12 8Z"/>,
 file:<><path d="M5 3h9l5 5v13H5ZM14 3v6h5M8 13h8m-8 4h6"/></>,
 link:<><path d="m9 8 3-3a5 5 0 0 1 7 7l-3 3M8 9l-3 3a5 5 0 0 0 7 7l3-3m-6-1 6-6"/></>
 };return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{p[name]||p.grid}</svg>;}
export function Bot({role,size=42,state}){const b=BOTS[role]||BOTS.manager;return <span className={'bot-avatar '+(state==='RUNNING'?'bot-working':'')} style={{'--bot-color':b.color,width:size,height:size}} aria-label={b.name+' icon'}><Icon name={b.glyph} size={Math.round(size*.47)}/>{state==='RUNNING'&&<i className="bot-pulse"/>}</span>;}
