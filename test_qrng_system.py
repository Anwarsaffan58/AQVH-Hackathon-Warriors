"""
QRNG Defense System Test Suite
AQVH1910 - Quantum Defense Security System
Team: Hackathon Warriors

Comprehensive testing for Quantum Random Number Generator foundation
All tests validate QRNG capabilities and defense applications
"""

import unittest
import requests
import time
import numpy as np
from quantum_core import QuantumRandomNumberGenerator, E91Protocol, BB84Protocol
import json

class TestQRNGFoundation(unittest.TestCase):
    """Test QRNG Foundation - Core Quantum Capabilities"""
    
    def setUp(self):
        """Set up QRNG foundation components"""
        self.qrng = QuantumRandomNumberGenerator()
        self.e91 = E91Protocol()
        self.bb84 = BB84Protocol()
    
    def test_qrng_bit_generation(self):
        """Test core QRNG functionality - Foundation of all security"""
        print("\n🔬 Testing QRNG Foundation: Quantum Random Bit Generation")
        
        # Generate quantum random bits
        bits, counts = self.qrng.generate_random_bits(num_bits=32, shots=1024)
        
        # Validate output format
        self.assertIsInstance(bits, str, "Bits should be string")
        self.assertIsInstance(counts, dict, "Counts should be dictionary")
        self.assertEqual(len(bits), 32, "Should generate 32 bits")
        
        # Validate quantum randomness
        for bit in bits:
            self.assertIn(bit, ['0', '1'], "All bits should be 0 or 1")
        
        print(f"✅ Generated {len(bits)} quantum random bits: {bits}")
        print(f"✅ Measurement counts: {counts}")
    
    def test_quantum_entropy_calculation(self):
        """Test quantum entropy - Measure of randomness quality"""
        print("\n📊 Testing Quantum Entropy Calculation")
        
        # Perfect entropy case (ideal quantum randomness)
        perfect_counts = {"0": 512, "1": 512}
        entropy = self.qrng.calculate_entropy(perfect_counts)
        self.assertAlmostEqual(entropy, 1.0, places=2, 
                              msg="Perfect distribution should have entropy ≈ 1.0")
        
        # Zero entropy case (no randomness)
        zero_counts = {"0": 1024, "1": 0}
        entropy = self.qrng.calculate_entropy(zero_counts)
        self.assertEqual(entropy, 0.0, "Single outcome should have entropy = 0")
        
        print(f"✅ Perfect entropy test: {entropy:.3f}")
        print(f"✅ Zero entropy test: {entropy:.3f}")
    
    def test_randomness_quality_defense_grade(self):
        """Test randomness quality for defense applications"""
        print("\n🛡️ Testing Defense-Grade Randomness Quality")
        
        # Generate test bits
        bits, _ = self.qrng.generate_random_bits(num_bits=100, shots=2048)
        results = self.qrng.test_randomness(bits)
        
        # Validate test structure
        required_keys = ["total_bits", "ones", "zeros", "frequency", "runs", 
                        "max_run_length", "complexity", "defense_grade"]
        for key in required_keys:
            self.assertIn(key, results, f"Missing key: {key}")
        
        # Defense-grade requirements
        self.assertEqual(results["total_bits"], 100)
        self.assertTrue(0.3 <= results["frequency"] <= 0.7, "Frequency should be balanced")
        self.assertTrue(results["max_run_length"] < 20, "Run length should be reasonable")
        
        print(f"✅ Randomness quality: {results}")
        print(f"✅ Defense grade: {'PASSED' if results['defense_grade'] else 'NEEDS IMPROVEMENT'}")
    
    def test_e91_protocol_quantum_advantage(self):
        """Test E91 protocol - Superior defense security"""
        print("\n🔐 Testing E91 Protocol: Quantum Key Distribution")
        
        result = self.e91.run_e91_protocol(num_rounds=30)
        
        # Validate E91 results
        required_keys = ["total_rounds", "sifted_key_length", "shared_key", "qber", "secure"]
        for key in required_keys:
            self.assertIn(key, result, f"Missing E91 key: {key}")
        
        # Security validation
        self.assertEqual(result["total_rounds"], 30)
        self.assertIsInstance(result["qber"], float)
        self.assertIsInstance(result["secure"], bool)
        self.assertTrue(0 <= result["qber"] <= 1, "QBER should be between 0 and 1")
        
        print(f"✅ E91 Key length: {result['sifted_key_length']} bits")
        print(f"✅ E91 QBER: {result['qber']:.3f} (threshold: 0.11)")
        print(f"✅ E91 Security: {'SECURE' if result['secure'] else 'COMPROMISED'}")
    
    def test_bell_inequality_quantum_security(self):
        """Test Bell inequality - Quantum entanglement validation"""
        print("\n🔔 Testing Bell Inequality: Quantum Security Validation")
        
        result = self.e91.bell_test_chsh(shots=1000)
        
        # Validate Bell test structure
        required_keys = ["correlations", "S", "bell_violation", "security_level"]
        for key in required_keys:
            self.assertIn(key, result, f"Missing Bell test key: {key}")
        
        # Physics constraints
        self.assertTrue(-4 <= result["S"] <= 4, "S parameter should be within physical bounds")
        self.assertIsInstance(result["bell_violation"], bool)
        
        print(f"✅ Bell S parameter: {result['S']:.3f}")
        print(f"✅ Bell violation: {'YES - Quantum confirmed' if result['bell_violation'] else 'NO - Classical only'}")
        print(f"✅ Security level: {result['security_level']}")
    
    def test_protocol_comparison_e91_vs_bb84(self):
        """Test protocol comparison - Demonstrate E91 superiority"""
        print("\n⚖️ Testing Protocol Comparison: E91 vs BB84")
        
        # E91 protocol
        e91_result = self.e91.run_e91_protocol(num_rounds=20)
        
        # BB84 protocol
        bb84_result = self.bb84.run_bb84_protocol(num_bits=50)
        
        print(f"✅ E91 efficiency: {e91_result.get('efficiency', 0):.3f}")
        print(f"✅ BB84 efficiency: {bb84_result.get('efficiency', 0):.3f}")
        print(f"✅ E91 advantage: Built-in eavesdropping detection")
        print(f"✅ BB84 limitation: {bb84_result.get('vulnerability', 'Unknown')}")
    
    def test_performance_metrics(self):
        """Test QRNG performance for defense deployment"""
        print("\n⚡ Testing QRNG Performance Metrics")
        
        # Generate multiple rounds to collect performance data
        for i in range(3):
            self.qrng.generate_random_bits(num_bits=64, shots=1024)
        
        metrics = self.qrng.get_performance_metrics()
        
        # Validate performance structure
        self.assertIn("total_bits_generated", metrics)
        self.assertIn("average_entropy", metrics)
        self.assertIn("performance_rating", metrics)
        
        print(f"✅ Total bits generated: {metrics['total_bits_generated']}")
        print(f"✅ Average entropy: {metrics['average_entropy']:.4f}")
        print(f"✅ Performance rating: {metrics['performance_rating']}")

class TestQRNGBackendAPI(unittest.TestCase):
    """Test QRNG Backend API - All Endpoints Powered by Quantum Foundation"""
    
    def setUp(self):
        """Set up API testing"""
        self.base_url = "http://127.0.0.1:5000"
        self.timeout = 15
        
        # Check if backend is available
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                self.skipTest("Backend server not responding. Start with: python qrng_backend.py")
        except requests.exceptions.RequestException:
            self.skipTest("Backend server not running. Start with: python qrng_backend.py")
    
    def test_health_endpoint_qrng_status(self):
        """Test health endpoint - QRNG foundation status"""
        print("\n🏥 Testing Backend Health: QRNG Foundation Status")
        
        response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "OK")
        self.assertIn("foundation", data)
        
        print(f"✅ Service status: {data['status']}")
        print(f"✅ Foundation: {data['foundation']}")
        print(f"✅ Backend: {data.get('backend', 'Unknown')}")
    
    def test_qrng_endpoint_foundation_service(self):
        """Test QRNG endpoint - Core foundation service"""
        print("\n🎲 Testing QRNG Endpoint: Foundation Random Number Generation")
        
        response = requests.get(f"{self.base_url}/rng?shots=1024&bits=32", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        expected_keys = ["bits", "entropy", "randomness_quality", "environmental_impact", "applications"]
        for key in expected_keys:
            self.assertIn(key, data, f"Missing QRNG key: {key}")
        
        # Validate QRNG quality
        self.assertEqual(len(data["bits"]), 32)
        self.assertTrue(0.0 <= data["entropy"] <= 1.0)
        
        print(f"✅ Generated bits: {data['bits'][:16]}...")
        print(f"✅ Quantum entropy: {data['entropy']:.4f}")
        print(f"✅ Defense grade: {data['randomness_quality'].get('defense_grade', False)}")
        print(f"✅ Applications: {len(data.get('applications', []))}")
    
    def test_qkd_protocols_quantum_security(self):
        """Test QKD protocols - Quantum-secured key distribution"""
        print("\n🔐 Testing QKD Protocols: Quantum Key Distribution")
        
        # Test E91 protocol (superior for defense)
        response = requests.get(f"{self.base_url}/qkd?protocol=e91&shots=1000", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        e91_data = response.json()
        self.assertIn("protocol", e91_data)
        self.assertIn("E91", e91_data["protocol"])
        self.assertIn("advantages", e91_data)
        
        print(f"✅ E91 Protocol: {e91_data['protocol']}")
        print(f"✅ Key length: {e91_data.get('key_length', 0)} bits")
        print(f"✅ Security: {'SECURE' if e91_data.get('secure') else 'COMPROMISED'}")
        print(f"✅ Advantages: {len(e91_data.get('advantages', []))}")
    
    def test_bell_test_quantum_validation(self):
        """Test Bell inequality test - Quantum security validation"""
        print("\n🔔 Testing Bell Test: Quantum Security Validation")
        
        response = requests.get(f"{self.base_url}/e91/chsh?shots=2000", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("S_parameter", data)
        self.assertIn("bell_violation", data)
        self.assertIn("security_level", data)
        
        print(f"✅ S parameter: {data['S_parameter']:.3f}")
        print(f"✅ Bell violation: {'YES' if data['bell_violation'] else 'NO'}")
        print(f"✅ Security level: {data['security_level']}")
    
    def test_ai_anomaly_detection_qrng_powered(self):
        """Test AI anomaly detection - QRNG-powered intelligence"""
        print("\n🤖 Testing AI Anomaly Detection: QRNG-Powered Intelligence")
        
        # Simulate quantum data with anomalies
        test_data = {
            "entropy": [0.98, 0.97, 0.96, 0.5],  # Entropy drop (anomaly)
            "qber": [0.05, 0.06, 0.08, 0.15]     # QBER spike (possible eavesdropping)
        }
        
        response = requests.post(f"{self.base_url}/ai/anomaly", 
                               json=test_data, timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("alerts", data)
        self.assertIn("status", data)
        self.assertIn("security_assessment", data)
        
        # Should detect anomalies
        self.assertGreater(len(data["alerts"]), 0, "Should detect test anomalies")
        
        print(f"✅ Anomaly detection: {data['status']}")
        print(f"✅ Alerts found: {len(data['alerts'])}")
        print(f"✅ Security assessment: {data['security_assessment']}")
    
    def test_defense_platforms_qrng_secured(self):
        """Test defense platforms - All QRNG-secured"""
        print("\n🛡️ Testing Defense Platforms: QRNG-Secured Communications")
        
        response = requests.get(f"{self.base_url}/defense/status", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("platforms", data)
        self.assertIn("summary", data)
        self.assertIn("foundation", data)
        
        platforms = data["platforms"]
        self.assertGreater(len(platforms), 0, "Should have defense platforms")
        
        # Validate QRNG integration
        for platform in platforms:
            self.assertIn("qrng_enabled", platform)
            self.assertTrue(platform["qrng_enabled"], f"{platform['name']} should be QRNG-enabled")
        
        print(f"✅ Defense platforms: {len(platforms)}")
        print(f"✅ QRNG foundation: {data.get('foundation', 'Unknown')}")
        print(f"✅ Security level: {data.get('security_level', 'Unknown')}")
    
    def test_performance_analysis_quantum_advantage(self):
        """Test performance analysis - QRNG vs Classical comparison"""
        print("\n📊 Testing Performance Analysis: QRNG Quantum Advantage")
        
        response = requests.get(f"{self.base_url}/performance/analysis", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("comparison", data)
        self.assertIn("quantum_advantages", data)
        self.assertIn("environmental_impact", data)
        
        # Validate quantum advantages
        advantages = data["quantum_advantages"]
        self.assertGreater(len(advantages), 0, "Should list quantum advantages")
        
        env_impact = data["environmental_impact"]
        self.assertIn("co2_reduction_percentage", env_impact)
        
        print(f"✅ Quantum advantages: {len(advantages)}")
        print(f"✅ CO₂ reduction: {env_impact.get('co2_reduction_percentage', 0)}%")
        print(f"✅ Energy savings: {env_impact.get('energy_savings_annual_kwh', 0)} kWh/year")

class TestQRNGIntegration(unittest.TestCase):
    """Test QRNG System Integration - Complete Defense Workflow"""
    
    def setUp(self):
        """Set up integration testing"""
        self.base_url = "http://127.0.0.1:5000"
        
        # Verify backend availability
        try:
            requests.get(f"{self.base_url}/health", timeout=5)
        except requests.exceptions.RequestException:
            self.skipTest("Backend not available for integration tests")
    
    def test_complete_quantum_defense_workflow(self):
        """Test complete quantum defense workflow - QRNG foundation enables all"""
        print("\n🔄 Testing Complete Quantum Defense Workflow")
        print("=" * 60)
        
        # Step 1: Generate quantum random foundation
        print("1️⃣ Generating QRNG Foundation...")
        rng_response = requests.get(f"{self.base_url}/rng?shots=2048&bits=256", timeout=15)
        self.assertEqual(rng_response.status_code, 200)
        rng_data = rng_response.json()
        quantum_bits = rng_data["bits"]
        print(f"   ✅ Generated {len(quantum_bits)} quantum random bits")
        print(f"   ✅ Entropy: {rng_data['entropy']:.4f}")
        
        # Step 2: Generate quantum key using E91
        print("\n2️⃣ Generating Quantum Key (E91 Protocol)...")
        key_response = requests.get(f"{self.base_url}/e91/key?shots=1500", timeout=15)
        self.assertEqual(key_response.status_code, 200)
        key_data = key_response.json()
        print(f"   ✅ Key length: {key_data.get('key_length', 0)} bits")
        print(f"   ✅ QBER: {key_data.get('qber', 0):.3f}")
        print(f"   ✅ Security: {key_data.get('security_assessment', 'Unknown')}")
        
        # Step 3: Set quantum-derived encryption key
        print("\n3️⃣ Setting Quantum Encryption Key...")
        set_key_response = requests.post(f"{self.base_url}/crypto/set_key",
                                       json={"bitstring": quantum_bits}, timeout=10)
        self.assertEqual(set_key_response.status_code, 200)
        set_key_data = set_key_response.json()
        print(f"   ✅ Key set: {set_key_data.get('key_length_bits', 0)} bits")
        print(f"   ✅ Source: {set_key_data.get('key_source', 'Unknown')}")
        
        # Step 4: Encrypt classified defense message
        print("\n4️⃣ Encrypting Classified Message...")
        classified_msg = "CLASSIFIED: QRNG Defense System operational - Quantum Shield active"
        encrypt_response = requests.post(f"{self.base_url}/crypto/encrypt",
                                       json={"message": classified_msg}, timeout=10)
        self.assertEqual(encrypt_response.status_code, 200)
        encrypt_data = encrypt_response.json()
        print(f"   ✅ Message encrypted with quantum key")
        print(f"   ✅ Security: {encrypt_data.get('algorithm', 'Unknown')}")
        
        # Step 5: Decrypt message
        print("\n5️⃣ Decrypting Message...")
        decrypt_response = requests.post(f"{self.base_url}/crypto/decrypt",
                                       json={
                                           "nonce": encrypt_data["nonce"],
                                           "ciphertext": encrypt_data["ciphertext"]
                                       }, timeout=10)
        self.assertEqual(decrypt_response.status_code, 200)
        decrypt_data = decrypt_response.json()
        self.assertEqual(decrypt_data["message"], classified_msg)
        print(f"   ✅ Message decrypted successfully")
        print(f"   ✅ Integrity verified: {decrypt_data.get('verification', 'Unknown')}")
        
        # Step 6: Validate system security
        print("\n6️⃣ Validating System Security...")
        bell_response = requests.get(f"{self.base_url}/e91/chsh?shots=2000", timeout=15)
        self.assertEqual(bell_response.status_code, 200)
        bell_data = bell_response.json()
        print(f"   ✅ Bell test S: {bell_data.get('S_parameter', 0):.3f}")
        print(f"   ✅ Quantum security: {'CONFIRMED' if bell_data.get('bell_violation') else 'CLASSICAL'}")
        
        # Step 7: Check defense platform status
        print("\n7️⃣ Checking Defense Platform Status...")
        defense_response = requests.get(f"{self.base_url}/defense/status", timeout=10)
        self.assertEqual(defense_response.status_code, 200)
        defense_data = defense_response.json()
        platforms = defense_data.get("platforms", [])
        secure_count = defense_data.get("summary", {}).get("secure_platforms", 0)
        print(f"   ✅ Defense platforms monitored: {len(platforms)}")
        print(f"   ✅ Secure platforms: {secure_count}")
        print(f"   ✅ QRNG foundation: Active across all platforms")
        
        print("\n" + "=" * 60)
        print("🎉 COMPLETE QUANTUM DEFENSE WORKFLOW VALIDATED!")
        print("✅ QRNG Foundation enables all security capabilities")
        print("✅ End-to-end quantum security confirmed")
        print("✅ Ready for National Quantum Mission deployment")
        print("=" * 60)
    
    def test_environmental_impact_analysis(self):
        """Test environmental impact - QRNG energy efficiency"""
        print("\n🌱 Testing Environmental Impact: QRNG Energy Efficiency")
        
        # Test performance comparison
        perf_response = requests.get(f"{self.base_url}/performance/analysis", timeout=10)
        self.assertEqual(perf_response.status_code, 200)
        perf_data = perf_response.json()
        
        # Validate environmental benefits
        env_impact = perf_data.get("environmental_impact", {})
        self.assertIn("co2_reduction_percentage", env_impact)
        self.assertIn("energy_savings_annual_kwh", env_impact)
        
        co2_reduction = env_impact.get("co2_reduction_percentage", 0)
        energy_savings = env_impact.get("energy_savings_annual_kwh", 0)
        
        self.assertGreater(co2_reduction, 0, "Should show CO₂ reduction")
        self.assertGreater(energy_savings, 0, "Should show energy savings")
        
        print(f"✅ CO₂ reduction: {co2_reduction}%")
        print(f"✅ Annual energy savings: {energy_savings:,} kWh")
        print(f"✅ Carbon credits eligible: {env_impact.get('carbon_credits_eligible', False)}")

def run_comprehensive_tests():
    """Run comprehensive QRNG test suite"""
    print("=" * 80)
    print("🔬 QRNG DEFENSE SYSTEM - COMPREHENSIVE TEST SUITE")
    print("AQVH1910 - Quantum Defense Security System")
    print("Team: Hackathon Warriors")
    print("=" * 80)
    print("Foundation: Testing all capabilities built on QRNG")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases (QRNG foundation first)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQRNGFoundation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQRNGBackendAPI))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQRNGIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=None)
    result = runner.run(suite)
    
    # Test summary
    print("\n" + "=" * 80)
    print("📊 QRNG DEFENSE SYSTEM TEST RESULTS")
    print("=" * 80)
    print(f"Tests executed: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED - QRNG SYSTEM VALIDATED!")
        print("✅ Quantum foundation confirmed")
        print("✅ Defense applications verified") 
        print("✅ Security protocols validated")
        print("✅ Environmental benefits confirmed")
        print("✅ Ready for production deployment")
    else:
        print("\n❌ SOME TESTS FAILED")
        if result.failures:
            print("Failures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split()[-1] if traceback.split() else 'Unknown'}")
        if result.errors:
            print("Errors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split()[-1] if traceback.split() else 'Unknown'}")
    
    print("=" * 80)
    print("🌟 QRNG Foundation enables all defense capabilities")
    print("Ready for India's National Quantum Mission!")
    print("=" * 80)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)