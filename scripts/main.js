"use strict";

const { K1 } = require("../");
const program = require("./program");

(async function main() {
  const mode = (process.argv[2] ?? "").toLowerCase();
  const k1 = new K1();
  await k1.on();
  if (mode === "demo" || mode === "code") {
    await program.code(k1);
  } else {
    await program.main(k1);
  }
  await k1.end();
})();
