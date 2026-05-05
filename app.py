from flask import Flask, render_template, request, jsonify
import random
import math
import uuid

app = Flask(__name__)
app.secret_key = 'startup-game-secret'

# ===================== DỮ LIỆU CỐ ĐỊNH =====================
SCENARIOS = [
    {"id":1,"name":"📈 Tin tốt thị trường","delta":{"price":0.08,"hype":15,"transparency":0}},
    {"id":2,"name":"📉 Tin xấu thị trường","delta":{"price":-0.08,"hype":-15,"transparency":-5}},
    {"id":3,"name":"🏆 Được giải thưởng","delta":{"hype":20,"transparency":10}},
    {"id":4,"name":"⚠️ Rò rỉ dữ liệu","delta":{"hype":-20,"transparency":-15}},
    {"id":5,"name":"🤝 Đối tác chiến lược","delta":{"hype":15,"transparency":5,"price":0.05}},
    {"id":6,"name":"🔒 Audit bảo mật","delta":{"transparency":15,"hype":5}},
    {"id":7,"name":"📰 Truyền thông đưa tin","delta":{"hype":25,"transparency":-5}},
    {"id":8,"name":"💸 Đối thủ giảm giá","delta":{"price":-0.1,"hype":-10}},
    {"id":9,"name":"⚖️ Thanh tra đột xuất","delta":{"transparency":-10,"hype":-10}},
    {"id":10,"name":"🚀 Sản phẩm đột phá","delta":{"hype":30,"transparency":5,"price":0.1}},
]

ACTIVE_CARDS = [
    {"id":"A1","name":"🔥 Marketing Blitz","cost":2,"type":"red","desc":"Tăng Hype +25, giảm Transparency -5","effect":{"hype":25,"transparency":-5}},
    {"id":"A2","name":"📱 Viral Campaign","cost":3,"type":"red","desc":"Tăng Hype +40, giảm Transparency -10","effect":{"hype":40,"transparency":-10}},
    {"id":"A3","name":"💰 Flash Sale","cost":2,"type":"red","desc":"Giảm giá 15%, tăng Hype +15","effect":{"price_percent":-15,"hype":15}},
    {"id":"A4","name":"⭐ Influencer Deal","cost":2,"type":"red","desc":"Tăng Hype +20","effect":{"hype":20}},
    {"id":"A5","name":"🎁 Airdrop","cost":3,"type":"red","desc":"Tăng Hype +30, tốn chi phí","effect":{"hype":30,"cost":10000}},
    {"id":"A6","name":"📢 PR Campaign","cost":2,"type":"red","desc":"Tăng Hype +15, Visibility +10","effect":{"hype":15}},
    {"id":"A7","name":"💎 Community Building","cost":1,"type":"green","desc":"Tăng Transparency +10","effect":{"transparency":10}},
    {"id":"A8","name":"🔍 Third Party Audit","cost":2,"type":"green","desc":"Tăng Transparency +20","effect":{"transparency":20}},
    {"id":"A9","name":"📊 Open Book","cost":2,"type":"green","desc":"Tăng Transparency +25, tốn chi phí","effect":{"transparency":25,"cost":5000}},
    {"id":"A10","name":"🛡️ Bug Bounty","cost":1,"type":"green","desc":"Tăng Transparency +8","effect":{"transparency":8}},
    {"id":"A11","name":"📝 Transparency Report","cost":2,"type":"green","desc":"Tăng Transparency +15, giảm Hype -5","effect":{"transparency":15,"hype":-5}},
    {"id":"A12","name":"🤝 Investor Call","cost":1,"type":"green","desc":"Tăng Transparency +5, tăng Hype +5","effect":{"transparency":5,"hype":5}},
    {"id":"A13","name":"💎 Token Buyback","cost":3,"type":"purple","desc":"Tăng Funding 10%, tốn chi phí","effect":{"funding_boost":0.1,"cost":20000}},
    {"id":"A14","name":"🏦 Secondary Offering","cost":3,"type":"purple","desc":"Tăng Funding 20%","effect":{"funding_boost":0.2}},
    {"id":"A15","name":"🗳️ DAO Vote","cost":2,"type":"purple","desc":"Tăng Transparency +5, Trust +5","effect":{"transparency":5}},
    {"id":"A16","name":"⛓️ Staking Launch","cost":2,"type":"purple","desc":"Tăng Utility","effect":{"utility":15}},
    {"id":"A17","name":"🏦 Treasury Diversify","cost":2,"type":"purple","desc":"Giảm rủi ro","effect":{"risk_reduce":10}},
    {"id":"A18","name":"📈 Strategic Partnership","cost":2,"type":"purple","desc":"Tăng Trust +10, Funding +5%","effect":{"funding_boost":0.05}},
    {"id":"A19","name":"🔥 Token Burn","cost":2,"type":"purple","desc":"Tăng Hype +10, Utility +10","effect":{"hype":10}},
    {"id":"A20","name":"🎁 Airdrop to Holders","cost":2,"type":"purple","desc":"Tăng Trust +10, Hype +10","effect":{"hype":10}},
    {"id":"A21","name":"💪 Cost Cutting","cost":1,"type":"green","desc":"Giảm chi phí 5%","effect":{"cost_reduce":0.05}},
    {"id":"A22","name":"🚀 FOMO Campaign","cost":2,"type":"red","desc":"Tăng Hype +25, Funding +5%","effect":{"hype":25,"funding_boost":0.05}},
]

REACTION_CARDS = [
    {"id":"R1","name":"🔒 Lock-up Extension","desc":"Giảm bán tháo khi bot rút","cost":5000},
    {"id":"R2","name":"📢 Emergency PR","desc":"Giảm 50% damage từ tin xấu","cost":3000},
    {"id":"R3","name":"🐋 Whale Whisperer","desc":"Tăng trust của nhà đầu tư lớn","cost":10000},
    {"id":"R4","name":"🩹 Damage Control","desc":"Tăng transparency +10","cost":2000},
]

# Tạo 50 bot đầu tư
random.seed(42)
BOTS = []
for i in range(1, 51):
    bot_type = random.choices(["FOMO", "Value Hunter", "Whale", "Retail"], weights=[40, 30, 10, 20])[0]
    wealth = random.randint(50000, 500000)
    BOTS.append({
        "id": i,
        "type": bot_type,
        "wealth": wealth,
        "hype_sens": random.uniform(0.5, 2.0),
        "trans_sens": random.uniform(0.5, 2.0),
    })

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def calculate_metrics(proj):
    # Tính toán các chỉ số cơ bản
    revenue_monthly = proj["units_m1"] * proj["price"]
    cost_monthly = proj["fixed_cost"] + proj["marketing_cost"]
    profit = revenue_monthly - cost_monthly
    
    # Intrinsic value dựa trên profit margin
    if revenue_monthly > 0:
        margin = profit / revenue_monthly
        intrinsic = clamp(margin * 100, 0, 100)
    else:
        intrinsic = 0
    
    # Runway (số tháng có thể hoạt động)
    monthly_burn = max(cost_monthly, 1000)
    runway = proj.get("available_cash", proj["owner_equity"]) / monthly_burn
    
    # Funding progress
    funding_progress = proj.get("funding_progress", 0)
    
    return {
        "intrinsic": intrinsic,
        "profit": profit,
        "runway": runway,
        "funding_progress": funding_progress,
        "available_cash": proj.get("available_cash", proj["owner_equity"])
    }

def attractiveness(project, bot, metrics):
    # Tính điểm hấp dẫn của dự án đối với bot
    score = 50
    
    # FOMO bot thích Hype
    if bot["type"] == "FOMO":
        score += project["hype"] * 0.3 * bot["hype_sens"]
    
    # Value Hunter thích Transparency và profit
    if bot["type"] == "Value Hunter":
        score += project["transparency"] * 0.3 * bot["trans_sens"]
        score += metrics["intrinsic"] * 0.2
    
    # Whale thích cả hai
    if bot["type"] == "Whale":
        score += project["hype"] * 0.2 * bot["hype_sens"]
        score += project["transparency"] * 0.2 * bot["trans_sens"]
    
    # Retail thì random hơn
    if bot["type"] == "Retail":
        score += project["hype"] * 0.15
        score += project["transparency"] * 0.15
    
    # Thêm nhiễu ngẫu nhiên
    score += random.uniform(-10, 10)
    
    return clamp(score, 0, 100)

def final_score(proj, phases_used):
    if proj["funding_progress"] < 0.3:
        return 0
    
    funding_score = proj["funding_progress"] * 50
    hype_score = proj["hype"] * 0.3
    trans_score = proj["transparency"] * 0.2
    
    raw_score = funding_score + hype_score + trans_score
    
    # Bonus nếu kết thúc sớm
    speed_bonus = max(0, (proj["max_phase"] - phases_used) * 2)
    
    return raw_score + speed_bonus

# Lưu trữ phòng
rooms = {}

@app.route('/')
def index():
    return render_template('host.html')

@app.route('/play/<room_id>/<int:player_index>')
def play_page(room_id, player_index):
    if room_id not in rooms:
        return "Phòng không tồn tại", 404
    room = rooms[room_id]
    if player_index < 0 or player_index >= room['num_players']:
        return "Chỉ số người chơi không hợp lệ", 400
    if room['players'][player_index] is not None:
        return "Slot này đã có người chơi", 400
    return render_template('play.html', room_id=room_id, player_index=player_index, max_players=room['num_players'])

@app.route('/api/create_room', methods=['POST'])
def create_room():
    data = request.json
    num_players = data.get('num_players', 4)
    if num_players < 2 or num_players > 10:
        num_players = 4
    
    room_id = str(uuid.uuid4())[:8]
    base_url = request.host_url.rstrip('/')
    join_links = [f"{base_url}/play/{room_id}/{i}" for i in range(num_players)]
    
    rooms[room_id] = {
        'num_players': num_players,
        'players': [None] * num_players,
        'phase': 0,
        'max_phase': 0,
        'status': 'waiting',  # waiting -> choosing_deck -> playing -> ended
        'bot_alloc': None,
        'logs': [],
        'player_ready': [False] * num_players,
        'pending_cards': {},
        'game_ended': False,
        'round_logs': []
    }
    
    return jsonify({'room_id': room_id, 'join_links': join_links})

@app.route('/api/submit_project', methods=['POST'])
def submit_project():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    project_data = data['project']
    
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_id]
    
    # Khởi tạo các giá trị mặc định cho project
    project_data['trust_scores'] = {bot['id']: 50 for bot in BOTS}
    project_data['status'] = 'active'
    project_data['funding_progress'] = 0
    project_data['total_invested'] = 0
    project_data['available_cash'] = project_data['owner_equity']
    project_data['current_phase'] = 0
    project_data['active_deck'] = []
    project_data['reaction_hand'] = []
    project_data['current_hand'] = []
    project_data['energy_left'] = 3
    project_data['hype'] = 50
    project_data['transparency'] = 50
    
    room['players'][player_index] = project_data
    room['player_ready'][player_index] = True
    
    # Kiểm tra nếu tất cả đã submit project
    if all(p is not None for p in room['players']):
        room['status'] = 'choosing_deck'
        room['player_ready'] = [False] * room['num_players']
        room['logs'].append("✅ Tất cả người chơi đã gửi dự án! Đang chờ chọn bài...")
    
    return jsonify({'ok': True})

@app.route('/api/submit_deck', methods=['POST'])
def submit_deck():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    active_indices = data['active_indices']
    reaction_indices = data['reaction_indices']
    
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_id]
    
    if len(active_indices) != 22:
        return jsonify({'error': 'Phải chọn đúng 22 lá Active'}), 400
    
    proj = room['players'][player_index]
    proj['active_deck'] = [ACTIVE_CARDS[i] for i in active_indices]
    proj['reaction_hand'] = [REACTION_CARDS[i] for i in reaction_indices[:3]]
    
    room['player_ready'][player_index] = True
    room['logs'].append(f"👤 Player {player_index + 1} đã chọn xong deck")
    
    # Kiểm tra nếu tất cả đã chọn deck
    if all(room['player_ready']):
        room['logs'].append("🎮 TẤT CẢ ĐÃ SẴN SÀNG! BẮT ĐẦU GAME...")
        
        # Khởi tạo game
        max_phase = 7  # Mặc định 7 phases
        room['max_phase'] = max_phase
        
        # Khởi tạo phân bổ bot
        bot_alloc = []
        for bot in BOTS:
            per = [0] * room['num_players']
            bot_alloc.append({'bot_id': bot['id'], 'perProject': per, 'idle': bot['wealth']})
        room['bot_alloc'] = bot_alloc
        
        # Khởi tạo phase đầu tiên
        room['phase'] = 1
        room['status'] = 'playing'
        room['player_ready'] = [False] * room['num_players']
        room['pending_cards'] = {}
        room['mulligan_used'] = [False] * room['num_players']
        
        # Phát bài ban đầu cho mỗi player
        for idx, p in enumerate(room['players']):
            if p:
                p['current_hand'] = random.sample(p['active_deck'], min(5, len(p['active_deck'])))
                p['energy_left'] = 3
                p['current_phase'] = 0
        
        room['logs'].append(f"🎮 GAME BẮT ĐẦU! Phase {room['phase']}/{room['max_phase']}")
        return jsonify({'ok': True, 'game_started': True})
    
    return jsonify({'ok': True, 'game_started': False})

@app.route('/api/card_lists', methods=['GET'])
def card_lists():
    return jsonify({'active': ACTIVE_CARDS, 'reaction': REACTION_CARDS})

@app.route('/api/host_state', methods=['GET'])
def host_state():
    room_id = request.args.get('room_id')
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_id]
    rankings = []
    
    for i, proj in enumerate(room['players']):
        if proj:
            metrics = calculate_metrics(proj)
            ended = proj.get('current_phase', 0) >= proj['max_phase']
            score = final_score(proj, proj.get('current_phase', 0)) if ended else 0
            
            rankings.append({
                'name': f"Player {i+1}",
                'funding': proj['funding_progress'],
                'hype': proj['hype'],
                'transparency': proj['transparency'],
                'score': score,
                'status': 'ended' if ended else 'playing',
                'current_phase': proj.get('current_phase', 0),
                'max_phase': proj['max_phase']
            })
        else:
            rankings.append({'name': f"Player {i+1}", 'funding': 0, 'score': 0, 'status': 'not_joined'})
    
    # Kiểm tra game kết thúc
    all_ended = all(p is None or p.get('current_phase', 0) >= p['max_phase'] for p in room['players'])
    if room['status'] == 'playing' and (room['phase'] > room['max_phase'] or all_ended):
        room['game_ended'] = True
        room['status'] = 'ended'
        room['logs'].append("🏆 GAME KẾT THÚC! 🏆")
    
    return jsonify({
        'status': room['status'],
        'phase': room['phase'],
        'max_phase': room['max_phase'],
        'players_joined': sum(1 for p in room['players'] if p is not None),
        'max_players': room['num_players'],
        'logs': room.get('logs', []),
        'rankings': rankings,
        'all_ready': all(room['player_ready']) if room['status'] == 'playing' else False,
        'game_ended': room.get('game_ended', False)
    })

@app.route('/api/player_state', methods=['GET'])
def player_state():
    room_id = request.args.get('room_id')
    player_index = int(request.args.get('player_index', -1))
    
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_id]
    
    if player_index < 0 or player_index >= len(room['players']) or room['players'][player_index] is None:
        return jsonify({'error': 'Player not found'}), 404
    
    proj = room['players'][player_index]
    metrics = calculate_metrics(proj)
    
    # Lấy danh sách nhà đầu tư
    investors = []
    if room['bot_alloc']:
        for alloc in room['bot_alloc']:
            amount = alloc['perProject'][player_index]
            if amount > 0:
                bot = next((b for b in BOTS if b['id'] == alloc['bot_id']), None)
                if bot:
                    investors.append({'type': bot['type'], 'amount': amount})
    
    ended = proj.get('current_phase', 0) >= proj['max_phase']
    final_score_value = final_score(proj, proj['max_phase']) if ended else 0
    
    return jsonify({
        'status': room['status'],
        'phase': room['phase'],
        'max_phase': room['max_phase'],
        'last_scenario': proj.get('last_scenario', 'Chờ sự kiện...'),
        'metrics': metrics,
        'hype': proj['hype'],
        'transparency': proj['transparency'],
        'hand': proj.get('current_hand', []),
        'energy_left': proj.get('energy_left', 3),
        'investors': investors,
        'funding_progress': proj['funding_progress'],
        'available_cash': metrics['available_cash'],
        'game_ended': room.get('game_ended', False),
        'ended': ended,
        'final_score': final_score_value,
        'player_ready': room['player_ready'][player_index]
    })

@app.route('/api/play_card', methods=['POST'])
def play_card():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    card_index = data['card_index']
    
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_id]
    
    if room['status'] != 'playing':
        return jsonify({'error': 'Game not in playing'}), 400
    
    proj = room['players'][player_index]
    
    if card_index >= len(proj['current_hand']):
        return jsonify({'error': 'Invalid card'}), 400
    
    card = proj['current_hand'][card_index]
    cost = card['cost']
    
    if proj['energy_left'] < cost:
        return jsonify({'error': f'Không đủ năng lượng! Cần {cost} năng lượng'}), 400
    
    room['pending_cards'][player_index] = card
    proj['energy_left'] -= cost
    
    return jsonify({'ok': True})

@app.route('/api/player_ready_phase', methods=['POST'])
def player_ready_phase():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_id]
    
    if room['status'] != 'playing':
        return jsonify({'error': 'Not playing'}), 400
    
    room['player_ready'][player_index] = True
    
    return jsonify({'ok': True})

@app.route('/api/run_phase', methods=['POST'])
def run_phase():
    data = request.json
    room_id = data['room_id']
    
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_id]
    
    if room['status'] != 'playing':
        return jsonify({'error': 'Game not active'}), 400
    
    if not all(room['player_ready']):
        return jsonify({'error': 'Not all players ready'}), 400
    
    phase = room['phase']
    players = room['players']
    logs = []
    
    # XỬ LÝ TỪNG DỰ ÁN
    for idx, proj in enumerate(players):
        if not proj or proj.get('current_phase', 0) >= proj['max_phase']:
            continue
        
        # 1. Random sự kiện
        scenario = random.choice(SCENARIOS)
        proj['last_scenario'] = scenario['name']
        logs.append(f"📢 Dự án {idx+1}: {scenario['name']}")
        
        delta = scenario['delta']
        if 'price' in delta:
            proj['price'] *= (1 + delta['price'])
        if 'hype' in delta:
            proj['hype'] = clamp(proj['hype'] + delta['hype'], 0, 100)
        if 'transparency' in delta:
            proj['transparency'] = clamp(proj['transparency'] + delta['transparency'], 0, 100)
        
        # 2. Áp dụng thẻ đã chọn trong phase
        if idx in room['pending_cards']:
            card = room['pending_cards'][idx]
            if card:
                eff = card['effect']
                if 'hype' in eff:
                    proj['hype'] = clamp(proj['hype'] + eff['hype'], 0, 100)
                if 'transparency' in eff:
                    proj['transparency'] = clamp(proj['transparency'] + eff['transparency'], 0, 100)
                if 'price_percent' in eff:
                    proj['price'] *= (1 + eff['price_percent']/100)
                if 'funding_boost' in eff:
                    boost = eff['funding_boost'] * proj['target_funding']
                    proj['total_invested'] = proj.get('total_invested', 0) + boost
                    proj['available_cash'] = proj.get('available_cash', 0) + boost
                    proj['funding_progress'] = min(1.0, proj['total_invested'] / proj['target_funding'])
                if 'cost' in eff:
                    proj['available_cash'] -= eff['cost']
                logs.append(f"  🃏 Dự án {idx+1} đánh bài: {card['name']}")
        
        # 3. Cập nhật metrics và phase
        metrics = calculate_metrics(proj)
        proj['funding_progress'] = metrics['funding_progress']
        proj['current_phase'] = proj.get('current_phase', 0) + 1
        
        logs.append(f"  📊 Funding: {(proj['funding_progress']*100):.1f}% | Hype: {proj['hype']} | Trans: {proj['transparency']}")
        
        if proj['current_phase'] >= proj['max_phase']:
            logs.append(f"  🏁 Dự án {idx+1} KẾT THÚC!")
    
    # XỬ LÝ BOT ĐẦU TƯ
    if room['bot_alloc']:
        bot_alloc = room['bot_alloc']
        
        # Tính attractiveness cho mỗi bot với mỗi dự án
        A = {}
        for bot in BOTS:
            for idx, proj in enumerate(players):
                if not proj or proj.get('current_phase', 0) >= proj['max_phase'] or proj['funding_progress'] >= 1:
                    A[(bot['id'], idx)] = -1e9
                else:
                    metrics = calculate_metrics(proj)
                    A[(bot['id'], idx)] = attractiveness(proj, bot, metrics)
        
        # BOT ĐẦU TƯ MỚI
        for bot_idx, bot in enumerate(BOTS):
            alloc_entry = bot_alloc[bot_idx]
            idle = alloc_entry['idle']
            if idle <= 0:
                continue
            
            # Tìm dự án tốt nhất để đầu tư
            candidates = [i for i, p in enumerate(players) if p and p.get('current_phase', 0) < p['max_phase'] and p['funding_progress'] < 1]
            if not candidates:
                continue
            
            best_idx = max(candidates, key=lambda i: A[(bot['id'], i)])
            best_score = A[(bot['id'], best_idx)]
            
            # Đầu tư vào dự án tốt nhất
            invest_amount = min(idle * 0.1, players[best_idx]['target_funding'] * 0.1)
            if invest_amount > 0 and players[best_idx]['funding_progress'] < 1:
                players[best_idx]['total_invested'] = players[best_idx].get('total_invested', 0) + invest_amount
                players[best_idx]['available_cash'] = players[best_idx].get('available_cash', 0) + invest_amount
                players[best_idx]['funding_progress'] = min(1.0, players[best_idx]['total_invested'] / players[best_idx]['target_funding'])
                alloc_entry['perProject'][best_idx] += invest_amount
                alloc_entry['idle'] -= invest_amount
                logs.append(f"💰 Bot {bot['type']} đầu tư ${invest_amount:,.0f} vào dự án {best_idx+1}")
    
    # RESET CHO PHASE TIẾP THEO
    room['pending_cards'] = {}
    room['player_ready'] = [False] * room['num_players']
    room['phase'] += 1
    room['logs'] = logs + room.get('logs', [])[-20:]  # Giữ 20 log gần nhất
    
    # Phát bài mới cho phase tiếp theo
    if room['phase'] <= room['max_phase']:
        for idx, proj in enumerate(players):
            if proj and proj.get('current_phase', 0) < proj['max_phase'] and proj['funding_progress'] < 1:
                proj['current_hand'] = random.sample(proj['active_deck'], min(5, len(proj['active_deck'])))
                proj['energy_left'] = 3
                room['mulligan_used'][idx] = False
    
    # Kiểm tra game kết thúc
    all_ended = all(p is None or p.get('current_phase', 0) >= p['max_phase'] for p in players)
    game_ended = (room['phase'] > room['max_phase']) or all_ended
    
    if game_ended:
        room['game_ended'] = True
        room['status'] = 'ended'
        room['logs'].append("🏆 GAME KẾT THÚC! 🏆")
    
    return jsonify({
        'ended': game_ended,
        'phase': room['phase'],
        'logs': logs,
        'game_ended': game_ended
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
