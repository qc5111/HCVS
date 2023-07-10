# 压缩投票
def compress_vote(vote_result):
    timestamp = vote_result["timestamp"].to_bytes(8, byteorder="big")
    user_id = vote_result["user_id"].to_bytes(6, byteorder="big")
    vote_id = vote_result["vote_id"].to_bytes(4, byteorder="big")
    vote_result_int = vote_result["vote_result"].to_bytes(4, byteorder="big")
    vote_data = timestamp + user_id + vote_id + vote_result_int
    return vote_data


# 解压投票
def decompress_vote(vote_data):
    timestamp = int.from_bytes(vote_data[:8], byteorder="big")
    user_id = int.from_bytes(vote_data[8:14], byteorder="big")
    vote_id = int.from_bytes(vote_data[14:18], byteorder="big")
    vote_result_int = int.from_bytes(vote_data[18:22], byteorder="big")
    vote_result = bin(vote_result_int)[2:].zfill(32)
    vote_result = {"timestamp": timestamp, "user_id": user_id, "vote_id": vote_id, "vote_result_int": vote_result_int,
                   "vote_result": vote_result}
    return vote_result
