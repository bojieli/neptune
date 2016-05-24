import sys
from iotbx.file_reader import any_file
import scitbx_array_family_flex_ext

def show_space_group(g):
	ret = ""
	ret += str( [str(x) for x in g.all_ops() ] ) + "\n"
	#ret += str( [x.as_double_array() for x in g.all_ops() ] ) + "\n"
	#for x in g.all_ops():
	#	ret += str(x) + "\t" + str(x.as_double_array()) + "\n"
	ret += "\tCrystal system: " + g.crystal_system() + "\n"
	ret += "\tIT number: " + str(g.type().number()) + "\n"
	ret += "\tH-M notation: " + g.type().lookup_symbol() + "\n"
	ret += "\tHall notation: " + g.type().hall_symbol()
	return ret

def print_coord(l, element=''):
	for coord in l:
		print("\t" + element + "\t" + str(coord))

def transformation(site, rot):
	return (rot[0] * site[0] + rot[1] * site[1] + rot[2] * site[2] + rot[9],
		rot[3] * site[0] + rot[4] * site[1] + rot[5] * site[2] + rot[10],
		rot[6] * site[0] + rot[7] * site[1] + rot[8] * site[2] + rot[11])

def is_valid(site):
	for coord in site:
		if coord < 0 or coord > 1:
			return False
	return True

def is_valid_extended(site):
	outside_dim = False
	for coord in site:
		if coord < -1 or coord > 2:
			return False
		if coord < 0 or coord > 1:
			if outside_dim:
				return False
			outside_dim = True
	return True

def is_new(new_site, sites):
	for s in sites:
		dist = 0
		for i in range(0,3):
			dist += (new_site[i] - s[i]) * (new_site[i] - s[i])
		if dist < 1e-6:
			return False
	return True

def sites_after_symmetry(group, sites, valid_func):
	while True:
		changed = False
		for s in sites:
			for x in group.all_ops():
				rot = x.as_double_array()
				new_site = transformation(s, rot)
				if valid_func(new_site) and is_new(new_site, sites):
					sites.append(new_site)
		if not changed:
			break
	return sites

def module_one_coord(i):
	while i < 0:
		i += 1
	while i > 1:
		i -= 1
	return i

def module_one(s):
	return tuple([ module_one_coord(i) for i in s ])

def sites_mod_symmetry(group, sites):
	sites = [ module_one(s) for s in sites ]
	while True:
		changed = False
		for s in sites:
			for x in group.all_ops():
				rot = x.as_double_array()
				new_site = module_one(transformation(s, rot))
				if is_new(new_site, sites):
					sites.append(new_site)
		if not changed:
			break
	return sites

def get_all_elements(scas):
	return set([ sca.element_symbol() for sca in scas ])
def get_all_elements(scas):
	return set([ sca.element_symbol() for sca in scas ])

def show_structure(s):
	print("Unit cell: " + str(s.unit_cell().parameters()))
	print("Space group: " + show_space_group(s.space_group()))
	print("Point group: " + show_space_group(s.space_group().build_derived_point_group()))
	print("")
	print("Number of scatterers: " + str(s.sites_frac().size()))
	elements = get_all_elements(s.scatterers())
	print("Elements: " + str(elements))
	print("Fractional coordinates: ")
	for e in elements:
		sel = s.select(s.element_selection(e))
		print_coord(list(sel.sites_frac()), e)
	print("Cartesian coordinates: ")
	for e in elements:
		sel = s.select(s.element_selection(e))
		print_coord(list(sel.sites_frac()), e)
	print("")
	print("Fractional coordinates after all symmetry (in unit cell): ")
	for e in elements:
		sel = s.select(s.element_selection(e))
		sym_sites = sites_after_symmetry(s.space_group(), list(sel.sites_frac()), is_valid)
		print_coord(sym_sites, e)
	print("Cartesian coordinates after all symmetry: (in unit cell)")
	for e in elements:
		sel = s.select(s.element_selection(e))
		sym_sites = sites_after_symmetry(s.space_group(), list(sel.sites_frac()), is_valid)
		sym_sites_cart = [ s.unit_cell().orthogonalize(site) for site in sym_sites ]
		print_coord(sym_sites_cart, e)
	print("")
	#print("Fractional coordinates after all symmetry (extend to 6 adjacent unit cells): ")
	#for e in elements:
	#	sel = s.select(s.element_selection(e))
	#	sym_sites = sites_after_symmetry(s.space_group(), list(sel.sites_frac()), is_valid_extended)
	#	print_coord(sym_sites, e)
	#print("Cartesian coordinates after all symmetry (extend to 6 adjacent unit cells): ")
	#for e in elements:
	#	sel = s.select(s.element_selection(e))
	#	sym_sites = sites_after_symmetry(s.space_group(), list(sel.sites_frac()), is_valid_extended)
	#	sym_sites_cart = [ s.unit_cell().orthogonalize(site) for site in sym_sites ]
	#	print_coord(sym_sites_cart, e)
	#print("")
	print("Fractional coordinates after all symmetry (mod 1): ")
	for e in elements:
		sel = s.select(s.element_selection(e))
		sym_sites = sites_mod_symmetry(s.space_group(), list(sel.sites_frac()))
		print_coord(sym_sites, e)
	print("Cartesian coordinates after all symmetry (mod 1): ")
	for e in elements:
		sel = s.select(s.element_selection(e))
		sym_sites = sites_mod_symmetry(s.space_group(), list(sel.sites_frac()))
		sym_sites_cart = [ s.unit_cell().orthogonalize(site) for site in sym_sites ]
		print_coord(sym_sites_cart, e)

def show_model(m, maxnum=10):
	cnt = 0
	for k in m:
		if cnt >= maxnum:
			print("\t...")
			break
		if isinstance(m[k], scitbx_array_family_flex_ext.std_string):
			val = str(list(m[k]))
		else:
			val = str(m[k])
		print("\t" + str(k) + ": " + val.strip())
		cnt += 1

f = any_file(sys.argv[1])
structures = f.file_content.build_crystal_structures()
models = f.file_content.model()
for s in structures:
	print("=========================================")
	print("Structure NO: " + s)
	show_structure(structures[s])
	print("")
	maxnum = 20
	print("Original CIF properties: (max " + str(maxnum) + ")")
	show_model(models[s], maxnum)
