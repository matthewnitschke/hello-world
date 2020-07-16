const robot = require("robotjs");
const inquirer = require('inquirer');

function sumHex(hex) {
    var bigint = parseInt(hex, 16);
    var r = (bigint >> 16) & 255;
    var g = (bigint >> 8) & 255;
    var b = bigint & 255;

    return r + g + b;
}

let topLeft;
let bottomRight;

inquirer
    .prompt([
        {
            type: 'input',
            name: 'topLeft',
            validate: () => {
                topLeft = robot.getMousePos();
                return true;
            }
        },
        {
            type: 'input',
            name: 'bottomRight',
            validate: () => {
                bottomRight = robot.getMousePos();
                return true;
            }
        }
    ])
    .then(() => {
        let w = bottomRight.x - topLeft.x;
        let h = bottomRight.y - topLeft.y;

        let img = robot.screen.capture(
            topLeft.x, 
            topLeft.y, 
            w, 
            h
        );
        
        let sum = 0;
        for (let x = 0; x < w; x ++) {
            for (let y = 0; y < h; y++) {
                let pixelHex = img.colorAt(x, y);
                let pixelSum = sumHex(pixelHex);

                sum += pixelSum;
            }
        }

        console.log(sum)
    })