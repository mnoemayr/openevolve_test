# Import the modeling class
from Pynite import FEModel3D

# Create a new model
model = FEModel3D()

# Geometry
model.add_node('N1', 0.0, 0.0, 0.0)
model.add_node('N2', 300.0, 0.0, 0.0)

model.add_material('A36', E=29_000_000.0, G=11_200_000.0, nu=0.3, rho=0.283)
model.add_section('Wsect', A=10.0, Iy=100.0, Iz=200.0, J=5.0)

m1 = model.add_member('M1', i_node='N1', j_node='N2', material_name='A36', section_name='Wsect')

# Supports and loads
model.def_support('N1', support_DX=True, support_DY=True, support_DZ=True, support_RX=True, support_RY=True, support_RZ=True)
model.add_node_load('N2', direction='FZ', P=-5.0, case='D')

# Load combinations and analysis
model.add_load_combo('1.0D', {'D': 1.0})
model.analyze_linear(log=False)

# Results
uz = model.nodes['N2'].DZ['1.0D']
rxn = model.nodes['N1'].RxnFZ['1.0D']

print(model.nodes['N1'], model.nodes['N2'])
print(f"Vertical displacement at N2: {uz:.6f} in")
print(f"Reaction force at N1: {rxn:.2f} lb")