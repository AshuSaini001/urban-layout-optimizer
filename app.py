import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import math
import copy

# --- Constants & Rules ---
SITE_W, SITE_H = 200, 140
PLAZA_SIZE = 40
SETBACK = 10
MIN_BUILDING_GAP = 15
NEIGHBOR_RADIUS = 60

# Fixed Plaza Coordinates
PLAZA_X = (SITE_W - PLAZA_SIZE) / 2
PLAZA_Y = (SITE_H - PLAZA_SIZE) / 2
PLAZA_RECT = (PLAZA_X, PLAZA_Y, PLAZA_X + PLAZA_SIZE, PLAZA_Y + PLAZA_SIZE)

BUILDING_TYPES = {
    'A': {'dim': (30, 20), 'color': '#3498db'}, 
    'B': {'dim': (20, 20), 'color': '#e67e22'}
}

class Building:
    def __init__(self, x, y, width, height, b_type, b_id):
        self.id = b_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = b_type
    
    @property
    def bounds(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

# --- Geometry Helpers ---
def get_edge_distance(b1, b2):
    r1 = b1.bounds
    r2 = b2.bounds
    dx = max(0, r2[0] - r1[2], r1[0] - r2[2])
    dy = max(0, r2[1] - r1[3], r1[1] - r2[3])
    return math.sqrt(dx*dx + dy*dy)

def rect_overlap(r1, r2):
    return not (r1[2] <= r2[0] or r1[0] >= r2[2] or r1[3] <= r2[1] or r1[1] >= r2[3])

# --- Violation Reporter ---
def audit_layout(buildings):
    violations = []
    # 1. Boundary & Plaza
    for b in buildings:
        if (b.x < SETBACK or b.y < SETBACK or 
            b.x + b.width > SITE_W - SETBACK or 
            b.y + b.height > SITE_H - SETBACK):
            violations.append({'type': 'boundary', 'entity': b})
        if rect_overlap(b.bounds, PLAZA_RECT):
             violations.append({'type': 'plaza_overlap', 'entity': b})

    # 2. Separation
    for i, b1 in enumerate(buildings):
        for j in range(i + 1, len(buildings)):
            b2 = buildings[j]
            dist = get_edge_distance(b1, b2)
            if dist == 0:
                violations.append({'type': 'collision', 'a': b1, 'b': b2})
            elif dist < MIN_BUILDING_GAP:
                violations.append({'type': 'proximity', 'a': b1, 'b': b2, 'dist': dist})

    # 3. Neighbor Mix
    tower_bs = [b for b in buildings if b.type == 'B']
    for b in buildings:
        if b.type == 'A':
            has_neighbor = False
            for target in tower_bs:
                if target == b: continue
                if get_edge_distance(b, target) <= NEIGHBOR_RADIUS:
                    has_neighbor = True
                    break
            if not has_neighbor:
                violations.append({'type': 'neighbor_missing', 'entity': b})     
    return violations

# --- Optimization Engine ---
def calculate_energy(buildings):
    violations = audit_layout(buildings)
    penalty = 0
    for v in violations:
        if v['type'] == 'collision': penalty += 10000
        elif v['type'] == 'plaza_overlap': penalty += 10000
        elif v['type'] == 'boundary': penalty += 5000
        elif v['type'] == 'proximity': penalty += 1000
        elif v['type'] == 'neighbor_missing': penalty += 500 
    total_area = sum(b.width * b.height for b in buildings)
    return penalty - (total_area * 0.1)

def mutate(buildings, id_counter):
    action = random.choice(['move', 'move', 'swap_dim', 'delete', 'add'])
    new_buildings = copy.deepcopy(buildings)
    
    if not new_buildings and action != 'add': action = 'add'

    if action == 'move' and new_buildings:
        b = random.choice(new_buildings)
        b.x += random.uniform(-10, 10)
        b.y += random.uniform(-10, 10)
    elif action == 'swap_dim' and new_buildings:
        b = random.choice(new_buildings)
        b.width, b.height = b.height, b.width
    elif action == 'delete' and new_buildings:
        new_buildings.remove(random.choice(new_buildings))
    elif action == 'add':
        b_type = random.choice(['A', 'B'])
        dims = BUILDING_TYPES[b_type]['dim']
        w, h = dims if random.random() > 0.5 else (dims[1], dims[0])
        x = random.uniform(SETBACK, SITE_W - SETBACK - w)
        y = random.uniform(SETBACK, SITE_H - SETBACK - h)
        id_counter += 1
        new_buildings.append(Building(x, y, w, h, b_type, id_counter))
        
    return new_buildings, id_counter

def optimize_layout(steps=3000):
    current_buildings = []
    id_counter = 0
    for _ in range(10):
        b_type = random.choice(['A', 'B'])
        w, h = BUILDING_TYPES[b_type]['dim']
        x = random.uniform(0, SITE_W)
        y = random.uniform(0, SITE_H)
        id_counter += 1
        current_buildings.append(Building(x, y, w, h, b_type, id_counter))

    current_energy = calculate_energy(current_buildings)
    best_buildings = current_buildings
    best_energy = current_energy
    
    temp = 1000.0
    cooling_rate = 0.995
    
    # Progress bar in Streamlit
    progress_bar = st.progress(0)
    
    for i in range(steps):
        new_buildings, id_counter = mutate(current_buildings, id_counter)
        new_energy = calculate_energy(new_buildings)
        
        if new_energy < current_energy:
            accept = True
        else:
            delta = new_energy - current_energy
            prob = math.exp(-delta / temp)
            accept = random.random() < prob
            
        if accept:
            current_buildings = new_buildings
            current_energy = new_energy
            if current_energy < best_energy:
                best_energy = current_energy
                best_buildings = copy.deepcopy(current_buildings)
        
        temp *= cooling_rate
        if i % 100 == 0:
            progress_bar.progress(i / steps)
            
    progress_bar.empty()
    return best_buildings

# --- Visualization for Web ---
def create_figure(layouts):
    """
    Modified to RETURN a figure object instead of calling plt.show()
    """
    num = len(layouts)
    fig, axes = plt.subplots(1, num, figsize=(7 * num, 7))
    if num == 1: axes = [axes]

    for i, buildings in enumerate(layouts):
        ax = axes[i]
        
        # Site & Plaza
        ax.add_patch(patches.Rectangle((0, 0), SITE_W, SITE_H, lw=2, ec='black', fc='#f8f9fa'))
        ax.add_patch(patches.Rectangle((SETBACK, SETBACK), SITE_W-20, SITE_H-20, lw=1, ec='#ccc', ls='--', fill=False))
        px1, py1, px2, py2 = PLAZA_RECT
        ax.add_patch(patches.Rectangle((px1, py1), PLAZA_SIZE, PLAZA_SIZE, lw=2, ec='green', fc='#abebc6', alpha=0.5, hatch='..'))
        ax.text(px1+20, py1+20, "PLAZA", ha='center', va='center', color='#1d8348', fontweight='bold')

        # Buildings
        violations = audit_layout(buildings)
        problem_ids = [v['entity'].id for v in violations if 'entity' in v]
        collision_ids = []
        for v in violations:
             if 'a' in v: collision_ids.extend([v['a'].id, v['b'].id])

        for b in buildings:
            edge_color = '#333'
            line_width = 1
            if b.id in problem_ids or b.id in collision_ids:
                edge_color = 'red'
                line_width = 2
            
            fill_color = BUILDING_TYPES[b.type]['color']
            rect = patches.Rectangle((b.x, b.y), b.width, b.height, 
                                     lw=line_width, ec=edge_color, fc=fill_color, alpha=0.85)
            ax.add_patch(rect)
            ax.text(b.x + b.width/2, b.y + b.height/2, f"{b.type}", ha='center', va='center', color='white', fontsize=8)

        # Violations
        for v in violations:
            if v['type'] == 'proximity':
                b1, b2 = v['a'], v['b']
                c1 = (b1.x + b1.width/2, b1.y + b1.height/2)
                c2 = (b2.x + b2.width/2, b2.y + b2.height/2)
                ax.plot([c1[0], c2[0]], [c1[1], c2[1]], color='red', linewidth=2, linestyle='-')
                mx, my = (c1[0]+c2[0])/2, (c1[1]+c2[1])/2
                ax.text(mx, my, f"{v['dist']:.1f}m!", color='red', fontsize=8, fontweight='bold', backgroundcolor='white')
            elif v['type'] == 'neighbor_missing':
                b = v['entity']
                circle = patches.Circle((b.x + b.width/2, b.y + b.height/2), NEIGHBOR_RADIUS, 
                                        fill=False, edgecolor='red', linestyle=':', alpha=0.5)
                ax.add_patch(circle)

        valid = len(violations) == 0
        status_color = 'green' if valid else 'red'
        status_text = "VALID" if valid else f"VIOLATIONS: {len(violations)}"
        stats = f"Count: {len(buildings)} | Area: {sum(b.width*b.height for b in buildings)}m²"
        
        ax.set_title(f"Result {i+1}: {status_text}", color=status_color, fontweight='bold')
        ax.text(5, SITE_H + 5, stats, fontsize=9, verticalalignment='bottom')
        ax.set_xlim(-5, SITE_W + 5)
        ax.set_ylim(-5, SITE_H + 30)
        ax.set_aspect('equal')
        ax.axis('off')
        
    return fig

# --- STREAMLIT UI ---
st.set_page_config(page_title="Urban Layout Optimizer", layout="wide")

st.title("🏗️ Generative Urban Layout Optimizer")
st.markdown("Uses **Simulated Annealing** to place buildings while respecting setbacks, plaza exclusion, and neighbor rules.")

# Sidebar controls
st.sidebar.header("Parameters")
num_layouts = st.sidebar.slider("Number of Layouts", 1, 5, 2)
steps = st.sidebar.slider("Optimization Steps", 1000, 10000, 3000)

if st.button("Generate Layouts"):
    results = []
    
    with st.spinner(f"Running optimization ({steps} steps)..."):
        for k in range(num_layouts):
            final_layout = optimize_layout(steps=steps)
            results.append(final_layout)
    
    # Generate Plot
    fig = create_figure(results)
    
    # Display in Streamlit
    st.pyplot(fig)
    st.success("Generation Complete!")