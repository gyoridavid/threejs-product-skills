// Shared browser launcher for the tools in this folder.
//
// Uses the installed Google Chrome by default. Set CHROME_PATH to use another
// Chromium-based browser (for example Playwright's own Chromium build).

import { chromium } from "playwright-core";

export async function launchBrowser(extraArgs = []) {
  const options = {
    headless: true,
    args: [
      "--autoplay-policy=no-user-gesture-required",
      "--ignore-gpu-blocklist",
      "--enable-unsafe-swiftshader",
      ...extraArgs,
    ],
  };
  if (process.env.CHROME_PATH) options.executablePath = process.env.CHROME_PATH;
  else options.channel = "chrome";

  try {
    return await chromium.launch(options);
  } catch (error) {
    throw new Error(
      `Could not start Chrome (${error.message.split("\n")[0]}).\n` +
        "Install Google Chrome, or set CHROME_PATH to a Chromium-based browser.",
    );
  }
}

export function parseArgs(argv, defaults) {
  const args = { ...defaults, _: [] };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (!arg.startsWith("--")) {
      args._.push(arg);
      continue;
    }
    const key = arg.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) args[key] = true;
    else {
      args[key] = next;
      i++;
    }
  }
  return args;
}
