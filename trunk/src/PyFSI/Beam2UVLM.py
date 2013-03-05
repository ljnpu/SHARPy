'''@package PyFSI.Beam2UVLM
@brief      Displacement extrapolation from beam FEM to UVLM grid.
@author     Rob Simpson
@contact    r.simpson11@imperial.ac.uk 
@version    0.0
@date       18/01/2013
@pre        None
@warning    None
'''

import numpy as np
import ctypes as ct
import SharPySettings as Settings
from PyBeam.Utils.XbeamLib import Psi2TransMat
from PyBeam.Utils.XbeamLib import Skew
from PyBeam.Utils.XbeamLib import Tangential
from PyAero.UVLM.Utils import DerivedTypesAero

def isodd(num):
    """@brief returns True if Num is odd"""
    return bool(num & 1)

def CoincidentGrid(PosDefor, PsiDefor, Section,\
                   VelA_A, OmegaA_A, PosDotDef, PsiDotDef,
                   XBINPUT, AeroGrid, AeroVels,\
                   OriginA_G = None,\
                   PsiA_G = None):
    """@brief Creates aero grid and velocities 
    centred on beam nodes.
    @param PosDefor Array of beam nodal displacements.
    @param PsiDefor Array of beam nodal rotations.
    @param Section Array containing sectional camberline coordinates.
    @param VelA_A Velocity of a-frame projected in a-frame.
    @param OmegaA_A Angular vel of a-frame projected in a-frame.
    @param PosDotDef Array of beam nodal velocities.
    @param PsiDotDef Array of beam nodal angular velocities.
    @param XBINPUT Beam input options.
    @param AeroGrid Aerodynamic grid to be updated.
    @param AeroVels Aerodynamic grid velocities to be updated
    @param OriginA_G Origin of a-frame.
    @param PsiA_G Attitude of a-frame w.r.t earth. 
    
    @details All displacements and velocities are projected in A-frame.
    All Omegas are 'inertial' angular velocities, so their magnitudes are not 
    affected by what frame they are projected in (objectivity).
    @warning TODO: take into account orientation of a-frame so that aero
    grid is projected in G-frame.
    """
    
    NumNodesElem = XBINPUT.NumNodesElem
            
    for iNode in range(PosDefor.shape[0]):
        "Work out what element we are in (works for 2 and 3-noded)"
        if iNode == 0:
            iElem = 0
        elif iNode < PosDefor.shape[0]-1:
            iElem = int(iNode/(NumNodesElem-1))
        elif iNode == PosDefor.shape[0]-1:
            iElem = int((iNode-1)/(NumNodesElem-1))
            
        "Work out what sub-element node we are in"
        if NumNodesElem == 2:
            if iNode < PosDefor.shape[0]-1:
                iiElem = 0
            elif iNode == PosDefor.shape[0]-1:
                iiElem = 1
                
        elif NumNodesElem == 3:
            iiElem = 0
            if iNode == PosDefor.shape[0]-1:
                iiElem = 2 
            elif isodd(iNode):
                iiElem = 1
        
        "Calculate transformation matrix for each node"
        CaB = Psi2TransMat(PsiDefor[iElem,iiElem,:])
        
        "loop through section coordinates"
        for jSection in range(Section.shape[0]):
            "Calculate instantaneous aero grid points"
            AeroGrid[jSection,iNode,:] = PosDefor[iNode,:] \
                                         + np.dot(CaB,Section[jSection,:])
                                         
            "Calc inertial angular velocity of B-frame projected in B-frame"
            Omega_B_B = np.dot( Tangential(PsiDefor[iElem,iiElem,:]) \
                        , PsiDotDef[iElem,iiElem,:] ) \
                        + np.dot(CaB.T, OmegaA_A)
                        
            "Calc inertial velocity at grid points (projected in A-frame.)"                             
            AeroVels[jSection,iNode,:] = VelA_A \
                        + np.dot(Skew(OmegaA_A),PosDefor[iNode,:]) \
                        + PosDotDef[iNode,:] \
                        + np.dot(CaB, np.dot(\
                        Skew(Omega_B_B), Section[jSection,:] ))
            
        #END for jSection
    #END for iNode
    
    if ( (OriginA_G != None) and (PsiA_G != None) ):
        "get transformation from a-frame to earth frame"
        CGa = Psi2TransMat(PsiA_G)
        
        "add the origin to grids in earth frame and transform vels"
        for iNode in range(PosDefor.shape[0]):
            for jSection in range(Section.shape[0]):
                AeroGrid[jSection,iNode,:] = OriginA_G + \
                                             np.dot(CGa,\
                                             AeroGrid[jSection,iNode,:])
                                             
                AeroVels[jSection,iNode,:] = np.dot(\
                                             CGa,AeroVels[jSection,iNode,:])
            #END for jSection
        #END for iNode
    #END if    

def CoincidentGridForce(XBINPUT, PsiDefor, Section, AeroForces,\
                        BeamForces):
    """@brief Creates aero grid and velocities 
    centred on beam nodes.
    @param XBINPUT Beam input options.
    @param PsiDefor Array of beam nodal rotations.
    @param Section Array containing sectional camberline coordinates.
    @param AeroForces Aerodynamic grid forces to be mapped to beam nodes.
    @param BeamForces BeamForces to overwrite.
    
    @details All Beam forces calculated in in a-frame, while aero forces 
    are defined in earth frame. 
    @warning TODO: take into account orientation of a-frame."""
    
    "zero beam forces"
    BeamForces[:,:] = 0.0
    
    "NumNodes per element"
    NumNodesElem = XBINPUT.NumNodesElem
    
    
    "loop along beam length"
    for iNode in range(XBINPUT.NumNodesTot):
        
        "Work out what element we are in (works for 2 and 3-noded)"
        if iNode == 0:
            iElem = 0
        elif iNode < XBINPUT.NumNodesTot-1:
            iElem = int(iNode/(NumNodesElem-1))
        elif iNode == XBINPUT.NumNodesTot-1:
            iElem = int((iNode-1)/(NumNodesElem-1))
            
        "Work out what sub-element node we are in"
        if NumNodesElem == 2:
            if iNode < XBINPUT.NumNodesTot-1:
                iiElem = 0
            elif iNode == XBINPUT.NumNodesTot-1:
                iiElem = 1
                
        elif NumNodesElem == 3:
            iiElem = 0
            if iNode == XBINPUT.NumNodesTot-1:
                iiElem = 2 
            elif isodd(iNode):
                iiElem = 1
        
        "Calculate transformation matrix for each node"
        CaB = Psi2TransMat(PsiDefor[iElem,iiElem,:])
        
        
        "loop through each sectional coordinate"
        for jSection in range(Section.shape[0]):
            
            "Get Section coord in a-frame"
            Section_A = np.dot(CaB,Section[jSection,:])
            
            "Calc moment"
            BeamForces[iNode,3:] += np.cross(Section_A,\
                                         AeroForces[jSection][iNode][:])
            
            "Calc force"
            BeamForces[iNode,:3] += AeroForces[jSection][iNode][:]
        
        # END for jSection
    #END for iNode

def InitSection(VMOPTS,VMINPUT,ElasticAxis):
    """@brief Initialise section based on aero & aeroelastic elastic options.
    @param VMOPTS UVLM solver options.
    @param VMINPUT UVLM solver inputs.
    @param ElasticAxis Position of elastic axis, defined as Theodorsen's a 
    parameter - i.e the number of semi-chords aft of midchord.
    @return Section cross section coordinates."""
    
    Section = np.zeros((VMOPTS.M.value+1,3),ct.c_double,'C')
    
    "calculate rotation due to twist"
    Psi = np.zeros((3))
    Psi[0] = VMINPUT.theta
    
    "get transformation matrix"
    R = Psi2TransMat(Psi)
    
    
    "get delta chord"
    DeltaC = VMINPUT.c/VMOPTS.M.value
    
    
    "get UVLM discretisation offset"
    Offset = 0.25*DeltaC
    
    
    "based on elastic axis at (z= 0, y = 0) get leading edge position"
    LeadingEdge = 0.5*VMINPUT.c + ElasticAxis*0.5*VMINPUT.c - Offset
    
    "calculate section coordinates"
    for j in range(VMOPTS.M.value+1):
        Section[j,:] = np.dot(R,[0.0,LeadingEdge-j*DeltaC,0.0])
        
    return Section
 

if __name__ == '__main__':
    import DerivedTypes
    XBINPUT = DerivedTypes.Xbinput(3,1)
    AeroM = 1
    
    "Initialise for Beam"
    PosDefor = np.zeros((XBINPUT.NumNodesTot,3),ct.c_double,'F')
    for i in range(PosDefor.shape[0]):
        PosDefor[i,0] = i
         
    PosDotDef = np.zeros((XBINPUT.NumNodesTot,3),ct.c_double,'F')
    
    PsiDefor = np.zeros((XBINPUT.NumElems,Settings.MaxElNod,3),\
                         dtype=ct.c_double, order='F')
    
    PsiDotDef = np.zeros((XBINPUT.NumElems,Settings.MaxElNod,3),\
                         dtype=ct.c_double, order='F')
    
    VelA_A = np.zeros(3)
    OmegaA_A = np.zeros(3)
    
    BeamForces = np.zeros((XBINPUT.NumNodesTot,6),ct.c_double,'F')
    
    "Initialise data for UVLM"
    VMOPTS = DerivedTypesAero.VMopts(1,1,True)
    VMINPUT = DerivedTypesAero.VMinput(1.0, 1.0, 25.0, 2.0*np.pi/180.0, \
                                             0.0*np.pi/180.0)
    
    Section = InitSection(VMOPTS,VMINPUT,ElasticAxis=-0.5)
    
    AeroGrid = np.zeros((Section.shape[0],PosDefor.shape[0],3),ct.c_double,'C')
    AeroVels = np.zeros((Section.shape[0],PosDefor.shape[0],3),ct.c_double,'C')
    
    CoincidentGrid(PosDefor, PsiDefor, Section, VelA_A, \
                   OmegaA_A, PosDotDef, PsiDotDef, XBINPUT,\
                   AeroGrid, AeroVels)
    
    print(AeroGrid, '\n')
    
    "Create forces"
    AeroForces = np.zeros((AeroM+1,XBINPUT.NumNodesTot,3),ct.c_double,'C')
    AeroForces[:,:,2] = 1.0
    
    "map to beam forces"
    CoincidentGridForce(XBINPUT, PsiDefor, Section, AeroForces,\
                        BeamForces)
    
    print(BeamForces, "\n")
    
    
    "forces must be reset"
    BeamForces[:,:] = 0.0
    
    "rotate by 90 degrees and check"
    PsiDefor[:,:,0] = np.pi/2.0
    
    "create updated grid"
    CoincidentGrid(PosDefor, PsiDefor, Section, VelA_A, \
                   OmegaA_A, PosDotDef, PsiDotDef, XBINPUT,\
                   AeroGrid, AeroVels)
    
    print(AeroGrid, '\n')
    
    "map to beam forces"
    CoincidentGridForce(XBINPUT, PsiDefor, Section, AeroForces,\
                        BeamForces)
    
    print(BeamForces, "\n")
    
    "check applied forces"
    "declare temp traids"
    Psi = np.zeros((3))
    
    "loop through all beam nodes"
    BeamForceCheck = np.zeros((3))
    for iNode in range(XBINPUT.NumNodesTot):
        BeamForceCheck[:] += BeamForces[iNode,:3]
    
    "account for rotation of aerodynamic FoR (freestream velocity)"
    Psi[0] = VMINPUT.alpha
    
    "get transformation matrix"
    CalphaG = Psi2TransMat(Psi)
    
    print(np.dot(CalphaG,BeamForceCheck))
    
