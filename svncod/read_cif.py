import sys
from iotbx.file_reader import any_file
import scitbx_array_family_flex_ext
import json

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

def print_coord_cif(l, element=''):
	cnt = 1
	for coord in l:
		print("\t" + element + str(cnt) + "\t" + "\t".join([ str(c) for c in coord]))
		cnt += 1

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

def sites_replicate_3(sites):
	new_sites = []
	for s in sites:
		for i in range(-1,2):
			for j in range(-1,2):
				for k in range(-1,2):
					new_sites.append(tuple([s[0]+i, s[1]+j, s[2]+k]))
	return new_sites


def get_all_elements(scas):
	return set([ sca.element_symbol() for sca in scas ])
def get_all_elements(scas):
	return set([ sca.element_symbol() for sca in scas ])

def get_symmetry_structure(s):
	elements = get_all_elements(s.scatterers())
	ns = s.customized_copy()
	for e in elements:
		sel = s.select(s.element_selection(e))
		sym_sites = sites_mod_symmetry(s.space_group(), list(sel.sites_frac()))
		sca = sel.scatterers()[0]
		for coord in sym_sites:
			sca.site = coord
			ns.add_scatterer(sca)
	return ns

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
	#print("Fractional coordinates after all symmetry (in unit cell): ")
	#for e in elements:
	#	sel = s.select(s.element_selection(e))
	#	sym_sites = sites_after_symmetry(s.space_group(), list(sel.sites_frac()), is_valid)
	#	print_coord(sym_sites, e)
	#print("Cartesian coordinates after all symmetry: (in unit cell)")
	#for e in elements:
	#	sel = s.select(s.element_selection(e))
	#	sym_sites = sites_after_symmetry(s.space_group(), list(sel.sites_frac()), is_valid)
	#	sym_sites_cart = [ s.unit_cell().orthogonalize(site) for site in sym_sites ]
	#	print_coord(sym_sites_cart, e)
	#print("")
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

	ns = s.expand_to_p1(sites_mod_positive=True)

	#ns = s.customized_copy()
	#for e in elements:
	#	sel = s.select(s.element_selection(e))
	#	sym_sites = sites_mod_symmetry(s.space_group(), list(sel.sites_frac()))
	#	sca = sel.scatterers()[0]
	#	for coord in sym_sites:
	#		sca.site = coord
	#		ns.add_scatterer(sca)

	print("Fractional coordinates after all symmetry (mod 1): ")
	for e in elements:
		sel = ns.select(ns.element_selection(e))
		print_coord(list(sel.sites_frac()), e)

	#print("Cartesian coordinates after all symmetry (mod 1): ")
	#for e in elements:
	#	sel = s.select(s.element_selection(e))
	#	sym_sites = sites_mod_symmetry(s.space_group(), list(sel.sites_frac()))
	#	sym_sites_cart = [ s.unit_cell().orthogonalize(site) for site in sym_sites ]
	#	print_coord(sym_sites_cart, e)

	#print("Fractional coordinates after all symmetry (mod 1): CIF format")
	#for e in elements:
	#	sel = s.select(s.element_selection(e))
	#	sym_sites = sites_mod_symmetry(s.space_group(), list(sel.sites_frac()))
	#	print_coord_cif(sym_sites, e)
	#print("Fractional coordinates after all symmetry (mod 3): CIF format")
	#for e in elements:
	#	sel = s.select(s.element_selection(e))
	#	sym_sites = sites_replicate_3(sites_mod_symmetry(s.space_group(), list(sel.sites_frac())))
	#	print_coord_cif(sym_sites, e)

	print("CIF block: ")
	print("===============================================")
	print(ns.as_cif_block())
	return ns

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

def replace_cif_scatterers(old, new):
	replaced = ""
	lines = old.split("\n")
	in_loop = False
	reading_headers = False
	skip_loop = False
	header_count = 0
	for line in lines:
		if in_loop and not reading_headers:
			if line.strip().startswith("_"):
				in_loop = False
			if line.strip() == "loop_":
				in_loop = False

		if in_loop and reading_headers:
			if header_count == 0:
				if line.strip().startswith("_atom_"):
					skip_loop = True
				if line.strip().startswith("_symmetry_"):
					skip_loop = True

				if not skip_loop:
					replaced += "loop_" + "\n"
			if not line.strip().startswith("_"):
				# we are in data section
				reading_headers = False
			else:
				header_count += 1

		if in_loop and skip_loop:
				continue

		if line.startswith("_cell_"):
			continue
		if line.startswith("_symmetry_"):
			continue
		if line.strip() == "loop_":
			in_loop = True
			reading_headers = True
			header_count = 0
			skip_loop = False
			continue

		replaced += line + "\n"
	replaced += new
	return replaced

def get_coord_frac(s, elements):
	l = []
	for e in elements:
		sel = s.select(s.element_selection(e))
		for site in list(sel.sites_frac()):
			l.append((e, site))
	return l

def get_coord_cart(s, elements):
	l = []
	for e in elements:
		sel = s.select(s.element_selection(e))
		for site in list(sel.sites_cart()):
			l.append((e, site))
	return l

def structure_json(name, s, ns, new_cif_block):
	obj = {}
	obj["name"] = name
	obj["unit_cell"] = s.unit_cell().parameters()
	obj["crystal_system"] = s.space_group().crystal_system()
	obj["space_group"] = s.space_group().type().lookup_symbol()
	obj["point_group"] = s.space_group().build_derived_point_group().type().lookup_symbol()

	obj["scatterer_count"] = ns.sites_frac().size()
	elements = get_all_elements(s.scatterers())
	obj["element_list"] = list(elements)
	obj["fractional_coordinates"] = get_coord_frac(ns, elements)
	obj["cartesian_coordinates"]  = get_coord_cart(ns, elements)

	obj["structures"] = [
		{"cif": str(s), "type": "original"},
		{"cif": new_cif_block,  "type": "symmetry"}
	]
	return json.dumps(obj)



f = any_file(sys.argv[1])
structures = f.file_content.build_crystal_structures()
models = f.file_content.model()
for s in structures:
	#print("=========================================")
	#print("Structure name: " + s)
	show_structure(structures[s])
	ns = get_symmetry_structure(structures[s])
	#print("")
	#print("New CIF block:")
	new_cif_block = replace_cif_scatterers(str(models[s]), str(ns.as_cif_block()))
	#print(new_cif_block)
	#print("JSON:")
	json = structure_json(s, structures[s], ns, new_cif_block)
	print(json)
	#show_model(models[s], 1000)
	
