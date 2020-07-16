const robot = require("robotjs");


// Get mouse position.
const mouse = robot.getMousePos();

// Get pixel color in hex format.
const hex = robot.getPixelColor(mouse.x, mouse.y);

console.log("#" + hex + " at x:" + mouse.x + " y:" + mouse.y);