import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Xe Tăng 2D", layout="centered")
st.title("🪖 Game Bắn Xe Tăng 2D (Battle City Classic)")

parts = [
    "<!DOCTYPE html><html><head><meta charset='utf-8'>",
    "<style>body{margin:0;text-align:center;font-family:sans-serif;background:#0f0f1a;color:white;}",
    "canvas{background:#111;display:block;margin:10px auto;border-radius:12px;box-shadow:0 8px 20px rgba(0,0,0,0.6);cursor:crosshair;}</style>",
    "</head><body><canvas id='c' width='480' height='480'></canvas><script>",
    "const cvs=document.getElementById('c'),ctx=cvs.getContext('2d');",
    "let score=0,lives=3,gameOver=false,healCounter=0,lastShotTime=0;",
    "let player={x:200,y:400,size:28,speed:2,dir:0,color:'#FF5964',hp:10,maxHp:10};",
    "let bullets=[],enemies=[],keys={};",
    "let mapGrid=[[0,0,0,0,0,0,0,0,0,0,0,0],[0,1,1,0,2,2,0,1,1,0,0,0],[0,1,0,0,0,0,0,0,1,1,0,0],[0,0,0,1,1,1,1,0,0,0,0,0],[0,2,0,1,0,0,1,0,2,2,0,0],[0,0,0,1,0,0,1,0,0,0,0,0],[0,0,0,0,1,1,0,0,0,0,0,0],[0,1,1,0,0,0,0,1,1,0,2,0],[0,0,0,0,0,0,0,0,0,0,0,0],[0,0,2,2,0,0,2,2,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0]];",
    "let tileSize=40;",
    "window.addEventListener('keydown',e=>{keys[e.code]=true;});",
    "window.addEventListener('keyup',e=>{keys[e.code]=false;});",
    "cvs.addEventListener('click',()=>{if(gameOver)return;let now=Date.now();if(now-lastShotTime>=200){lastShotTime=now;shootPlayer();}});",
    "function shootPlayer(){let bx=player.x+player.size/2,by=player.y+player.size/2,bdx=0,bdy=0;",
    "if(player.dir===0)bdy=-5;else if(player.dir===1)bdx=5;else if(player.dir===2)bdy=5;else if(player.dir===3)bdx=-5;",
    "bullets.push({x:bx-4,y:by-4,w:8,h:8,dx:bdx,dy:bdy,fromPlayer:true});}",
    "function checkCollision(x,y,size){let left=x,right=x+size,top=y,bottom=y+size;",
    "if(left<0||right>cvs.width||top<0||bottom>cvs.height)return true;",
    "let
