function e(e){var r;if(!e||"object"!=typeof e)return null;const o=e;if("string"==typeof o.code)return o.code;const t=o.response;if(t){const e=t.data;if(e){const o=null!=(r=e.error)?r:e.errors;if(o&&"string"==typeof o.code)return o.code;if("string"==typeof e.code)return e.code}}return null}export{e};
//# sourceMappingURL=errorHandling-B5S82HA9.js.map
