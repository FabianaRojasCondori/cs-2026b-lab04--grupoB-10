// Evaluación local de grabaciones: bloquear conexiones salientes del proceso Node.
// Se carga antes de promptfoo. No se usa para proveedores remotos ni para instalar.
'use strict';
const bloquear = () => { throw new Error('Evaluación offline: conexión de red bloqueada'); };
globalThis.fetch = async () => { throw new Error('Evaluación offline: fetch bloqueado'); };
for (const protocolo of ['node:http', 'node:https']) {
  const modulo = require(protocolo);
  modulo.request = bloquear;
  modulo.get = bloquear;
}
const net = require('node:net');
net.Socket.prototype.connect = bloquear;
net.connect = bloquear;
net.createConnection = bloquear;
require('node:tls').connect = bloquear;
require('node:dgram').createSocket = bloquear;
process.env.PROMPTFOO_DISABLE_TELEMETRY = '1';
process.env.PROMPTFOO_DISABLE_UPDATE = '1';
process.env.PROMPTFOO_DISABLE_SHARING = '1';
