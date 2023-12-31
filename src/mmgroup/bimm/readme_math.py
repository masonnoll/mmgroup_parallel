r"""
Let :math:`\mbox{IncP3}` be the Coxeter group generated by the 
nodes :math:`P_i, L_i, 0 \leq i  < 13` of the projective plane 
:math:`\mbox{P3}` as above, and let :math:`\mbox{AutP3}` be the 
automorphism group of :math:`\mbox{P3}`. Let 
:math:`\,\mbox{IncP3}:\mbox{AutP3}\,` be the split extension of the
group :math:`\mbox{IncP3}` by the factor group :math:`\mbox{AutP3}`,
where :math:`\mbox{AutP3}` operates naturally on the generating
reflections of the Coxeter group :math:`\mbox{IncP3}`.

In this section we construct a mapping from
:math:`\,\mbox{IncP3}:\mbox{AutP3}\,`  to the Bimonster.

Therefore we use the Norton's presentation :cite:`Nor02` of the 
Monster. Then we follow the ideas in Farooq's thesis :cite:`Far12` 
for extending that presentation of the Monster to a homomorphism from 
the Coxeter group :math:`\mbox{IncP3}` to the Bimonster.
We assume that the reader is familiar with :cite:`Nor02` and 
we will adopt notation from ibid.


Norton's presentation of the Monster and the Bimonster
.......................................................


Norton :cite:`Nor02` defines a presentation :math:`(s,t,u,v,x,\alpha)`
of the group :math:`\mbox{IncP3}:\mbox{AutP3}`, where 
:math:`s,t,u \in \mbox{AutP3}`, :math:`v = \prod_{i=1}^{12} P_i`,  
:math:`x = P_0 L_0`, :math:`\alpha = P_0 v`. 
Then he adds a relation that maps :math:`\mbox{IncP3}` to the 
Bimonster :math:`\mathbb{M} \wr 2`, thus obtaining a presentation of
:math:`(\mathbb{M} \wr 2):\mbox{AutP3}`. Next he shows that
this is actually a presentation of the direct product 
:math:`(\mathbb{M} \wr 2) \times \mbox{AutP3}`. Then he adds a
set of relations that cancel the factor :math:`\mbox{AutP3}`, 
leading to a presentation of the Bimonster with the generators
:math:`(s,t,u,v,x,\alpha)`. It turns out that all these generators,
except for :math:`\alpha`, are in the subgroup
:math:`\mathbb{M} \times \mathbb{M}` of index 2 of the Bimonster
:math:`\mathbb{M} \wr 2`. Finally, he gives a further set of 
relations in the generators :math:`(s,t,u,v,x)` cancelling the second 
factor of the direct product :math:`\mathbb{M} \times \mathbb{M}`,
thus obtaining a presentation of the Monster :math:`\mathbb{M}`.
We remark that :math:`P_i^u = P_{i-1}` and  :math:`L_i^u = L_{i+1}`,
with indices to be taken modulo 13, so that  :math:`P_i` and 
:math:`L_i` can easily be computed from the generators
:math:`(s,t,u,v,x,\alpha)`.

Let :math:`\mbox{IncP3}^+` be the subgroup of :math:`\mbox{IncP3}` 
generated be the products of generators :math:`P_i, L_i` of 
:math:`\mbox{IncP3}` with an even number of factors. Then 
:math:`\mbox{IncP3}^+` has index 2 in :math:`\mbox{IncP3}`, and the
presentation :math:`(s,t,u,v,x)` together with the relations 
mentioned above defines a mapping :math:`\phi` 
from :math:`\mbox{IncP3}^+ : \mbox{AutP3}` into the Monster.


Mapping Norton's presentation into our representation of the Monster
.....................................................................

Essentially, our task is to construct an explicit mapping from the
generators :math:`(s,t,u,v,x,\alpha)`  of
:math:`\mbox{IncP3} : \mbox{AutP3}`
into the Bimonster :math:`\mathbb{M} \wr 2`.
A first step for achieving this goal is to actually construct a 
mapping  :math:`\phi` from
the generators :math:`(s,t,u,v,x)` of
:math:`\mbox{IncP3}^+ : \mbox{AutP3}` to :math:`\mathbb{M}`.


In :cite:`Nor02` for each point :math:`P_i` an element :math:`P^*_i`
of of the subgroup :math:`\mathbb{M} \times \mathbb{M}` of the
Bimonster is defined. The elements :math:`P^*_i` are called the 
*stars* (corresponding to the points :math:`P_i`); and it is shown 
that :math:`\mbox{AutP3}` permutes the stars :math:`P^*_i` in the 
same  way as it permutes the corresponding points.
Actually, the stars :math:`P^*_i` are defined as words of generators
:math:`P_i, L_i` of even length, modulo the relations defining the 
Bimonster.

According to :cite:`Nor02` we have :math:`\phi(x) = \tau` for the 
generator :math:`x`, where :math:`\tau` is  the triality element of the 
Monster. There it is also shown that the stars and the 
(products of an even number of) points map to elements of the 
extraspecial subgroup  :math:`Q_{x0}` (of structure :math:`2^{1+24}`) 
of the Monster. In :cite:`Nor02` explicit images of the points and 
stars in :math:`Q_{x0}` are constructed up to sign. More specifically,
the images of these elements are given in the Leech lattice modulo 2,
which is isomorphic to the quotient of :math:`Q_{x0}` by its centre
:math:`\{1, x_{-1}\}`.
It is easy to see that the signs of the images of the points and
stars may be chosen arbitrarily, with the only restriction that
the product :math:`P^*_0 P^*_1 P^*_3 P^*_9` must be mapped to
the element :math:`x_{\Omega}` of :math:`Q_{x0}`, and not to its
negative :math:`x_{-\Omega}`. It can be shown that the tuple
:math:`(P_0 P_1, \ldots, P_0 P_{12}, P^*_1,  \ldots, P^*_{12})`,
when taken modulo the centre of :math:`Q_{x0}`, corresponds to a 
basis of the Leech lattice modulo 2. So for defining the mapping 
:math:`\phi` on the points and the stars it suffices to specify
the signs of the images of the entries of that tuple. It turns out
that everything works fine if we declare all these signs to be
positive. This means that for any such  image 
:math:`x_d x_\delta \in Q_{x0}`, with
:math:`d \in \mathcal{P}, \delta \in C^*`, we choose :math:`d` to
be a 'positive' element of the Parker loop :math:`\mathcal{P}`,
according to our construction of :math:`\mathcal{P}`.
  
With this choice the mapping :math:`\phi` is uniquely defined
on the points and on the stars; and we shall see that it is
also uniquely defined on all generators :math:`(s,t,u,v,x)` 
of the presentation given in :cite:`Nor02`. The functions
``PointP3`` and ``StarP3`` in module 
``mmgroup.bimm.p3_to_mm`` compute the mapping :math:`\phi` on
the points and the stars, respectively.

The mapping :math:`\phi` is already defined on  :math:`x` and on
:math:`v` (since :math:`v` is a product of points). Generators
:math:`s,t,u,` are defined as automorphisms in :math:`\mbox{AutP3}`;
so it suffices compute :math:`\phi(a)` for :math:`a \in \mbox{AutP3}`.


It is also shown in :cite:`Nor02` that the images of elements of
:math:`\mbox{AutP3}` are in the centralizer  :math:`G_{x0}` 
(of structure :math:`2^{1+24}.\mbox{Co}_1`) of the element
:math:`x_{-1}`. Note that the images of the points and the stars
generate the group :math:`Q_{x0}`; so the action of any automorphism
in :math:`\mbox{AutP3}` is determined (as an element of 
:math:`G_{x0}`) by its action on the points and the stars, up to 
sign. The group :math:`\mbox{AutP3}` is the simple group 
:math:`L_3(3)` in ATLAS notation. Thus it is generated by its
elements of odd order. For any :math:`g \in G_{x0}` at most one
of the elements  :math:`g, x_{-1} \cdot g` has odd order, so that 
the correct image of any element of :math:`\mbox{AutP3}` of  odd
order (and hence the image of the any element of
:math:`\mbox{AutP3}`) in :math:`G_{x0}` is uniquely defined.
So we can also construct the images of the generators
:math:`(s,t,u)`. Function ``Norton_generators`` in module
``mmgroup.bimm.p3_to_mm`` returns the images of the generators
:math:`(s,t,u,v,x)` under our mapping :math:`\phi`.

Faaroq :cite:`Far12` had to perform strenuous calculations for
actually computing :math:`\phi` on :math:`\mbox{AutP3}`, since he 
had to use the representations of the groups :math:`G_{x0}` and
:math:`\mathbb{M}` available in 2012. With our construction of the
Monster and of :math:`G_{x0}` we are in a much more comfortable
situation. Function ``AutP3_MM`` in module ``mmgroup.bimm.p3_to_mm``
quickly computes the mapping :math:`\phi` on :math:`\mbox{AutP3}`. 
In the remainder of this subsection we discuss the operation of 
that function.

The relevant automorphsims :math:`a \in \mbox{AutP3}` are given as
mappings between the 13 points and the 13 stars, where the stars 
are  transformed in the same way as corresponding points. Using our 
contruction of :math:`\phi` on the points and the stars, the image 
:math:`\phi(a)`  can be given as an automorphism of  :math:`Q_{x0}` 
in  :math:`G_{x0}`, where :math:`G_{x0}` operates on :math:`Q_{x0}` 
by conjugation. Given such an automorphism :math:`\gamma` on 
:math:`Q_{x0}`, the C function ``xsp2co1_elem_from_mapping`` in file
``xsp2co1_map.c`` computes the corresponding element :math:`g` of 
the group :math:`G_{x0}` up to sign.

We close with some remarks on how the
C function ``xsp2co1_elem_from_mapping`` works.

Class ``Xsp2_Co1`` in module ``mmgroup.structures.xsp_co1`` wraps
fast C functions for computing in the group :math:`G_{x0}`, so that
computations in :math:`G_{x0}` are easy. Given an automorphism 
:math:`\gamma` of :math:`Q_{x0}` as above, we can easily compute the 
image :math:`\gamma(\tilde{\Omega})`, where :math:`\tilde{\Omega}` is 
the vector in the Leech lattice modulo 2 corresponding to the standard 
frame in the Leech lattice. The C function ``gen_leech2_reduce_type4``
in file ``gen_leech_reduce.c`` can compute an element 
:math:`h_1 \in G_{x0}` that maps :math:`\gamma(\tilde{\Omega})` to 
:math:`\tilde{\Omega}`, see section :ref:`computation-leech2` 
in the *guide for developers* for mathematical background. 
So if :math:`g \in G_{x0}` corresponds to the automorphism
:math:`\gamma` then  :math:`g h_1` corresponds to an automorphism
:math:`\gamma_1` of :math:`Q_{x0}` fixing  :math:`\tilde{\Omega}`. 
The stabilizer of :math:`\tilde{\Omega}` in  :math:`G_{x0}` is a 
group :math:`N_{x0}` of structure :math:`2^{1+24}.2^{11}.M_{24}`. 
The automorphism :math:`\gamma_1` can easily be computed from 
:math:`\gamma` and :math:`h_1`. So it remains the considerably 
simpler task to compute  an element of :math:`N_{x0}` corresponding
to the automorphism :math:`\gamma_1` of :math:`Q_{x0}`. This 
computation is done as  described in the documentation of the 
C function ``xsp2co1_elem_from_mapping``.



From the Monster to the Bimonster
.................................

In this section we construct a mapping :math:`\Phi` from the group
:math:`\,\mbox{IncP3} : \mbox{AutP3} \,` to the Bimonster using 
the mapping 
:math:`\phi : \mbox{IncP3}^+ : \mbox{AutP3} \rightarrow \mathbb{M}` 
defined in the last subsection. 

The generator 
:math:`\alpha` in :math:`\mbox{IncP3} \setminus \mbox{IncP3}^+`
is an involution that acts on :math:`\mbox{IncP3}^+` (and also on
:math:`\,\mbox{IncP3} ^+: \mbox{AutP3}`)  by conjugation. Hence
by Theorem 3.1 in :cite:`CNS88` there is a mapping :math:`\Phi` from
:math:`\,\mbox{IncP3} : \mbox{AutP3} \,` to the Bimonster
:math:`\mathbb{M} \wr 2` given by:

 .. math:: 

      \Phi(y) = (\phi(y), \phi(y^\alpha)) \in \mathbb{M} \times \mathbb{M}
      \,, \quad \mbox{for} \quad y \in \,\mbox{IncP3} ^+: \mbox{AutP3},


and :math:`\Phi(\alpha)` is the involution in :math:`\mathbb{M} \wr 2` 
swapping the two copies of :math:`\mathbb{M}`.
For simplicity, we will also write :math:`\alpha` for the element
:math:`\Phi(\alpha)` of :math:`\mathbb{M} \wr 2`.

Since :math:`\alpha = \prod_{i=0}^{12} P_i` commutes with all points
:math:`P_i` and also with :math:`\mbox{AutP3}`, we have:

 .. math:: 
     \Phi(P_i) = \alpha \cdot (\phi(\alpha \cdot P_i), 
     \phi(\alpha \cdot P_i)) \, , \\
     \Phi(a) =  (\phi(a), \phi(a)) \,, \quad \mbox{for} \;
     a \in \mbox{AutP3} \, .

It remains to compute :math:`\Phi(L_i)`. Here have to compute 
:math:`\phi(L_i^\alpha)`. Therefore we will use the follwing fact: 

It easy to show that the elements of the Bimonster
:math:`\mathbb{M} \wr 2` that are conjugate to :math:`\alpha` are 
precisely the elements of shape :math:`\alpha \cdot (m, m^{-1})`,
:math:`m \in \mathbb{M}`.

Since :math:`\Phi(P_0) = \alpha \cdot (\phi(\alpha \cdot P_0),
\phi(\alpha \cdot P_0))` holds for the involution :math:`P_0`, we
conclude that :math:`\Phi(P_0)` is conjugate to :math:`\alpha` in
:math:`\mathbb{M} \wr 2`. In a Coxeter group all nodes connected 
by a path of edges are conjugate; so the nodes :math:`\Phi(L_i)`
are also conjugate to  :math:`\alpha`. Together with the fact
stated above we obtain:

 .. math:: 

     \Phi(L_i) = \alpha \cdot (\phi(\alpha \cdot L_i), 
     \phi(\alpha \cdot L_i)^{-1}) \, .

Note that :math:`\phi(\alpha \cdot L_0) = \phi(v) \cdot \tau`, where
:math:`\tau` is the triality element in the Monster. Furthermore, we
have 

 .. math:: 

    \phi(\alpha \cdot L_i) = \phi(\alpha \cdot L_0)^{\phi(u)^i} \,.

"""

