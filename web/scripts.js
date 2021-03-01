"use strict";
document.addEventListener('DOMContentLoaded', setup);

const query = parse_query_string(window.location.search.substring(1));

const map = new Image();
map.src = query["m"];
map.onload = loaded;
map.onerror = loadfail;

let map_scale_factor = 1.1;
let map_scale = 0;
let map_pos_x = 0;
let map_pos_y = 0;


const anim_image = new Image();
anim_image.src = "images/montage.png";

const load_failed_image = new Image();
load_failed_image.src = "images/compass-broken.png";

const ANIM_FRAME_CT = 32;

let loading_anim;
let loading_anim_frame = 0;

let canvas;
let context;

let mouse_origin_x = 0;
let mouse_origin_y = 0;

let touch_delta = 0;



// setup ----------

function setup() {
    canvas = document.getElementById("map");
    context = canvas.getContext("2d");

    document.getElementById("loading").getContext("2d").imageSmoothingEnabled = false;
    
    loading_anim = setInterval(loading, 50);
    
    scaleCanvas();
}

function loaded() {
    // called when map image loads; remove loading icon and display map at default location
    clearInterval(loading_anim);
    document.getElementById("loading").remove();

    addEventListeners();
    scaleCanvas();
    
    resetView();
}

function loadfail() {
    clearInterval(loading_anim);
    let loading_ctx = document.getElementById("loading").getContext("2d");
    loading_ctx.drawImage(load_failed_image, 0, 0, 64, 64);
}

function loading() {
    // animate compass while map loads
    loading_anim_frame++;
    loading_anim_frame %= 32
    let loading_ctx = document.getElementById("loading").getContext("2d")
    loading_ctx.drawImage(anim_image, 0, 16 * loading_anim_frame, 16, 16, 0, 0, 64, 64)
}


function scaleCanvas() {
    // match size to window size to prevent blurring
    let w  = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    let h = window.innerHeight|| document.documentElement.clientHeight|| document.body.clientHeight;
    let ratio = window.devicePixelRatio;
    canvas.width = w
    canvas.height = h

    context.imageSmoothingEnabled = false;
}

function parse_query_string(query) {
    let lets = query.split("&");
    let query_string = {};
    for (let i = 0; i < lets.length; i++) {
        let pair = lets[i].split("=");
        let key = decodeURIComponent(pair[0]);
        let value = decodeURIComponent(pair[1]);
        // If first entry with this name
        if (typeof query_string[key] === "undefined") {
            query_string[key] = decodeURIComponent(value);
            // If second entry with this name
        } else if (typeof query_string[key] === "string") {
            let arr = [query_string[key], decodeURIComponent(value)];
            query_string[key] = arr;
            // If third or later entry with this name
        } else {
            query_string[key].push(decodeURIComponent(value));
        }
    }
    return query_string;
}


// rendering --------

function resetView() {
    // move map to default scale and location
    map_scale = 0;
    if (query['s'] != null) map_scale = Number(query['s']);
    map_pos_x = (canvas.width / 2) - (map.width / 2);
    if (query['x'] != null) map_pos_x = (canvas.width / 2) + Number(query['x']);
    map_pos_y = (canvas.height / 2) - (map.height / 2);
    if (query['y'] != null) map_pos_y = (canvas.height / 2) + Number(query['y']);
    drawmap();
}

function drawmap() {
    //paint the map on the canvas
    let scale = Math.pow(map_scale_factor, map_scale)
    context.clearRect(0, 0, canvas.width, canvas.height)
    context.drawImage(map, map_pos_x, map_pos_y, map.width * scale, map.height * scale)
    let w  = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
}



// interactivity --------

function getShareableLink() {
    let address = "" + window.location.protocol + "//";
    if(window.location.origin != "null") address = window.location.origin;
    address += window.location.pathname;
    address += "?";
    address += "m=" + query["m"];
    address += "&s=" + map_scale;
    address += "&x=" + Math.floor((map_pos_x - (canvas.width / 2)));
    address += "&y=" + Math.floor((map_pos_y - (canvas.height / 2)));
    return address;
}

function translationInput(x, y, move) {
        if(move){
            map_pos_x += x - mouse_origin_x;
            map_pos_y += y - mouse_origin_y;
            drawmap();
        }
        mouse_origin_x = x;
        mouse_origin_y = y;
}

function scaleInput(x, y, out) {
        // zoom in and out
        let rel_pos_x = map_pos_x - x
        let rel_pos_y = map_pos_y - y
        if (out) {
            map_scale++;
            rel_pos_x *= map_scale_factor;
            rel_pos_y *= map_scale_factor;
        }
        else {
            map_scale--;
            rel_pos_x /= map_scale_factor;
            rel_pos_y /= map_scale_factor;
        }
        map_pos_x = rel_pos_x + x
        map_pos_y = rel_pos_y + y
        drawmap();
}

function copyToClipBoardExtraJank(string) {
    let area = document.createElement("textarea");
    area.class = "copybox";
    area.value = string;
    document.body.appendChild(area);
    area.focus();
    area.select();
    try {
        
        document.execCommand("copy");
    } catch (e) {}
    area.remove();
}

function addEventListeners() {
    document.getElementById("body").addEventListener('mousemove', function(e){
        translationInput(e.clientX, e.clientY, e.buttons != 0);
    });
    
    document.getElementById("body").addEventListener('touchmove', e => {
        if (e.touches.length == 1){
            let touch = e.touches[0];
            translationInput(touch.clientX, touch.clientY, true);
        }
        else if (e.touches.length == 2){
            let threshold = 13.5;
            let new_delta = Math.sqrt(Math.pow(e.touches[1].clientX - e.touches[0].clientX, 2) + Math.pow(e.touches[1].clientY - e.touches[0].clientY, 2))
            let x = e.touches[0].clientX;//(e.touches[1].clientX + e.touches[0].clientX) / 2;
            let y = e.touches[0].clientY;//(e.touches[1].clientY + e.touches[0].clientY) / 2;
            translationInput(x, y, true);
            if(new_delta - touch_delta < -1 * threshold){
                scaleInput(x, y, false);
                touch_delta = new_delta;
            }
            else if(new_delta - touch_delta > threshold){
                scaleInput(x, y, true);
                touch_delta = new_delta;
            }
        }
    });

    document.getElementById("body").addEventListener('touchstart', e => {
        if (e.touches.length == 1){
            mouse_origin_x = e.touches[0].clientX;
            mouse_origin_y = e.touches[0].clientY;
        }
        else if (e.touches.length == 2){
            touch_delta = Math.sqrt(Math.pow(e.touches[1].clientX - e.touches[0].clientX, 2) + Math.pow(e.touches[1].clientY - e.touches[0].clientY, 2))
        }
    });
    
    document.getElementById("body").addEventListener('touchend', e => {
        if (e.touches.length == 1){
            mouse_origin_x = e.touches[0].clientX;
            mouse_origin_y = e.touches[0].clientY;
        }
    });

    document.getElementById("body").addEventListener('wheel', function(e){
        scaleInput(mouse_origin_x, mouse_origin_y, e.deltaY < 0);
    });

    // reset view when compass rose is clicked
    document.getElementById("rose").addEventListener("click", resetView);
    
    document.getElementById("link").addEventListener("click", e => {
        try {
        navigator.clipboard.writeText(getShareableLink());
        } catch (e) {}
    });


    // resize the canvas when the window is resized
    window.addEventListener("resize", function(){
        scaleCanvas();
        drawmap();
    })
}
