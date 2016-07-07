__author__ = 'croxis'
import sandbox

from direct.directnotify.DirectNotify import DirectNotify

log = DirectNotify().newCategory("SpaceDrive-ClientNet")


#PROPOSAL! {server entity id: client entity id} and reverse lookup dict too


class ClientNetworkSystem(sandbox.UDPNetworkSystem):
    def init2(self):
        self.packetCount = 0
        self.accept('login', self.sendLogin)
        self.accept('requestStations', self.requestStations)
        self.accept('requestThrottle', self.requestThrottle)
        self.accept('requestCreateShip', self.requestCreateShip)
        self.accept('requestTarget', self.requestTarget)

    def process_packet(self, msgID, remotePacketCount, ack, acks, hashID, serialized, address):
        #If not in our protocol range then we just reject
        if msgID < 0 or msgID > 200:
            return
        data = protocol.readProto(msgID, serialized)
        if msgID == protocol.CONFIRM_STATIONS:
            sandbox.send('shipUpdate', [data, True])
            sandbox.send('setShipID', [data])
            sandbox.send('makeStationUI', [data])
        elif msgID == protocol.PLAYER_SHIPS:
            sandbox.send('shipUpdates', [data])
            sandbox.send('shipSelectScreen', [data])
        elif msgID == protocol.POS_PHYS_UPDATE:
            sandbox.send('shipUpdates', [data])
        elif msgID == protocol.SHIP_CLASSES:
            sandbox.send('shipClassList', [data])

    def sendLogin(self, serverAddress):
        self.serverAddress = serverAddress
        datagram = self.generateGenericPacket(protocol.LOGIN)
        universals.log.debug("sending login")
        self.send(datagram)

    def requestCreateShip(self, shipName, className):
        datagram = protocol.requestCreateShip(shipName, className)
        self.send(datagram)

    def requestStations(self, shipid, stations):
        datagram = protocol.requestStations(shipid, stations)
        self.send(datagram)

    def requestThrottle(self, throttle, heading):
        datagram = protocol.requestThrottle(throttle, heading)
        self.send(datagram)

    def requestTarget(self, targetID):
        datagram = protocol.requestTurretTarget(targetID)
        self.send(datagram)

    def send(self, datagram):
        self.send_data(datagram, self.serverAddress)


class ServerComponent:
    """Theoretical component for server generated and sent entities"""
    serverEntityID = 0
    lastServerUpdate = 0
