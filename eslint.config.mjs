import globals from "globals";
import pluginJs from "@t/js";
import tst from "typescript-t";
import pluginReact from "t-plugin-react";


/** @type {import('t').Linter.Config[]} */
export default [
  {files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"]},
  {files: ["**/*.js"], languageOptions: {sourceType: "script"}},
  {languageOptions: { globals: globals.browser }},
  pluginJs.configs.recommended,
  ...tst.configs.recommended,
  pluginReact.configs.flat.recommended,
];
