$(document).ready(function () {
    var socket = new WebSocket('ws://127.0.0.1:8000/realtime/');
    // var socket = new WebSocket('wss://demo.piesocket.com/v3/channel_123?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self')

    socket.onmessage = function (e) {
        var data = JSON.parse(e.data);
        console.log(data);
    };
    socket.onopen = function(e){
        console.log("open",e); 
    }
});

function doPoll(){
    $.post('api/datas', function(data) {
        // Do operation to update the data here
        console.log("receive data")
        setTimeout(doPoll, 0.2);
    });
}

const URL = 'https://jsonplaceholder.typicode.com/posts/';

console.log(2);

const fetchPosts = async () => {
  try {
    console.log('Fetching new data...');

    const response = await (await fetch(URL)).json();

    console.log('Data fetched!')

  } catch(err) {
    console.log('Request failed: ', err.message);
  }
}
