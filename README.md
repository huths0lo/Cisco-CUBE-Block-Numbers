# Cisco-CUBE-Block-Numbers
Update Cisco CUBE routers to block inbound calls.

## Script Process
1. Log into golden router
2. Run 'show run | sec translation-rule 300'
3. Determine the highest rule # in the list
4. Increment $rulenumber by 1
5. Input from user (with validation to be sure it's a phone number entered).
6. Send commands back to routers using cube.txt list

## Things to Look For
I pull the initial configuration from a ```$GOLDENROUTER``` that serves as our master for the configuration.  
That way I don't have to poll each of the CUBE routers before applying the rule.  Seemed like a waste of time to me.
Update this value on line 68 to fit your needs.

The script assumes you are using voice translation-rule 300 for blocking inbound calls.  If you're using a different translation-rule, find and replace will be your best friend.

Script assumes 10 digit dialing, if you're outside North America you will need to adjust the error checking for your specific needs.

## Initial Configuration
Determine your inbound dial-peer using:   ```debug voice ccapi inout```
In this case we are using dial-peer voice 100 voip

### Cube.txt File
Update this file with the IP addresses of your CUBE routers, one per line.

### Dial Peer Configuration
```
dial-peer voice 100 voip
 description OUTBOUND TO SIP
 translation-profile incoming SIP-INBOUND
 translation-profile outgoing SIP-OUTBOUND
 call-block translation-profile incoming BLOCK_PSTN
 call-block disconnect-cause incoming unassigned-number
 rtp payload-type nse 99
 rtp payload-type nte 100
 session protocol sipv2
 session target sip-server
 destination e164-pattern-map 100
 incoming called-number ^[2-9].........$
 voice-class codec 1000  
 dtmf-relay rtp-nte
 no vad   
```

### Translation-rule Configuration
```
voice translation-rule 300
 rule 1 reject /5626398700/
 rule 2 reject /9122271259/
 rule 3 reject /9128224029/
```

### Translation Profile Configuration
```
voice translation-profile BLOCK_PSTN
translate calling 300
```

## Acknowledgements 
* Kirk Byers wrote **MOST** of the code used - [Netmiko](https://github.com/ktbyers/netmiko)
