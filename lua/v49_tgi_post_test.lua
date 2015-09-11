local bit = require("bit")
-- dissects the v49 Protocol (including the TGI specific fields)
-- we create a "protocol" for our tree
v49_proto = Proto("v49","Vita49","Vita 49 Protocol")

-- we create our fields
frameNum_field = ProtoField.float("FrameNum")

-- we add our fields to the protocol
v49_proto.fields = { frameNum_field }

-- then we register v49_proto as a postdissector
register_postdissector(v49_proto)

packetnum = -1

function v49_proto.dissector(buffer,pinfo,tree  )
    local log_tree = tree:add(v49_proto,"Log Msgs")
    
    pinfo.cols.protocol = "V49"
    packetnum = pinfo.number

    v49Header_offset = 42
    v49Header_length = 28
    v49Payload_offset = v49Header_offset + v49Header_length
    v49Payload_length = 480

    v49HeaderBuf = buffer(v49Header_offset,v49Header_length)
    local v49_packet = tree:add(v49_proto,buffer(),"Vita 49 ("..v49HeaderBuf:len()..")")
   
    --local subtree_header = v49_packet:add_le(buffer(v49Header_offset,v49Header_length), "V49 Header")
    local subtree_header = v49_packet:add_le(v49HeaderBuf, "V49 Header")
    subtree_header:add(buffer(0,2),"The first two bytes: " .. buffer(0,2):uint())

    tt = v49HeaderBuf:range(0, 4):le_uint()
    log_tree:add("v49Start: " .. tostring(tt))
    
    -- frameNum = v49HeaderBuf:range(5, 4):bitfield(20, 12):le_uint()
    range = v49HeaderBuf:range(5, 4)
    tt = range:bitfield(20, 12)
    frameNum = tt
    
    fixed_data = v49HeaderBuf:range(4, 4):le_uint()
    log_tree:add("fixed_data: " .. tostring(fixed_data))
    frameCnt = bit.rshift(fixed_data, 20)
    log_tree:add("FrameNum: " .. tostring(frameCnt))
    frameSize = bit.band(fixed_data, 0xfffff)
    log_tree:add("frameSize: " .. tostring(frameSize))

    v49HeaderBuf = buffer(v49Header_offset,v49Header_length)
    local subtree_payload = v49_packet:add_le(buffer(v49Payload_offset,v49Payload_length), "V49 Payload")
    
    local v49Start = 1448293433  -- '94SV'
    local v49End   = '444e4556'  -- 'DNEV'
    local FFTEnd   = '34127856'
    local wordSize = 4
    local frameDataOffset  = 1 * wordSize
    local packetDataOffset = 2 * wordSize
    local StreamBinOffset  = 3 * wordSize
    local timeOffset       = 4 * wordSize
    local freqOffset       = 5 * wordSize
    local payloadOffset    = 7 * wordSize
    local payloadSize      = 120 * wordSize

    local cnt = 0
    for i = 0, (buffer:len()-4) do
         fixed_data = buffer:range(i, 4):le_uint()
         if fixed_data == v49Start then
            cnt = cnt + 1
         end
    end
    v49_packet:add("Num V49 packets: " .. tostring(cnt))
    
    tree:add(frameNum_field, packetnum)
    log_tree:add("A subsequent Packet, Gap: ")
end


