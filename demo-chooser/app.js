var app = require('express')();
var http = require('http').createServer(app);
var io = require('socket.io')(http);
var path = require('path')

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + '/index.html'));
});

let usersData = {}

function getWinner() {
    let keys = Object.keys(usersData)
    let smallestCount = 999999999;
    let smallestName = "";
    for (let i = 0; i < keys.length; i ++) {
        let c = usersData[keys[i]]
        if (c < smallestCount) {
            smallestName = keys[i]
            smallestCount = c
        }
    }

    return smallestName
}

io.on('connection', (socket) => {
  console.log('a user connected');

  socket.on('client-update', (data) => {
      console.log(data);
      usersData[data.name] = data.taps
  })

  socket.on('admin-start', () => {
    io.emit('server-message', '3')
    setTimeout(() => {
        io.emit('server-message', '2')
        setTimeout(() => {
            io.emit('server-message', '1')
            setTimeout(() => {
                io.emit('server-message', 'START!')
                io.emit('server-start', true)

                let count = 5;
                let interval = setInterval(() => {
                    io.emit('server-message', count)
                    count--;

                    if (count <= -1){
                        clearInterval(interval)
                        io.emit('server-stop', true)
                        io.emit('server-message', `${getWinner()} goes next!`)
                    }
                }, 1000)
            }, 1000)
        }, 1000)
    }, 1000)
  })

  socket.on('admin-reset', () => {
      io.emit('server-reset')
      usersData = {}
  })
});

setInterval(() => {
    io.emit('server-update', usersData)
}, 500)

http.listen(3000, () => {
  console.log('listening on *:3000');
});