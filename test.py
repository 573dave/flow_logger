import random
from typing import List, Dict

# Optional: Disable logging for testing
FLOW_LOGGER_ENABLED = True

from core import flow_logger

@flow_logger
def generate_user_data(num_users: int) -> List[Dict]:
    """Generate sample user data."""
    users = []
    for i in range(num_users):
        user = {
            'id': i,
            'name': f'User_{i}',
            'age': random.randint(18, 80),
            'score': random.randint(0, 100)
        }
        users.append(user)
    return users

@flow_logger
def calculate_statistics(users: List[Dict]) -> Dict:
    """Calculate some basic statistics about the users."""
    if not users:
        return {}
    
    total_age = sum(user['age'] for user in users)
    total_score = sum(user['score'] for user in users)
    
    return {
        'avg_age': total_age / len(users),
        'avg_score': total_score / len(users),
        'num_users': len(users),
        'high_scorers': len([u for u in users if u['score'] > 80])
    }

@flow_logger
def process_statistics(stats: Dict) -> Dict:
    """Process the statistics and add some derived metrics."""
    if not stats:
        return {}
    
    # Simulate some processing time
    # import time
    # time.sleep(0.5)
    
    return {
        **stats,
        'score_quality': 'Good' if stats['avg_score'] > 70 else 'Poor',
        'age_group': 'Young' if stats['avg_age'] < 30 else 'Mature',
        'performance_metric': stats['high_scorers'] / stats['num_users'] * 100
    }

@flow_logger
def generate_report(processed_stats: Dict) -> str:
    """Generate a final report string."""
    if not processed_stats:
        return "No data available"
    
    # Simulate an error occasionally
    if processed_stats['performance_metric'] < 30:
        raise ValueError("Performance metric is too low!")
    
    report = f"""
    User Statistics Report
    ---------------------
    Number of Users: {processed_stats['num_users']}
    Average Age: {processed_stats['avg_age']:.1f}
    Average Score: {processed_stats['avg_score']:.1f}
    Score Quality: {processed_stats['score_quality']}
    Age Group: {processed_stats['age_group']}
    Performance: {processed_stats['performance_metric']:.1f}%
    """
    return report

def main():
    try:
        # Generate some test data
        users = generate_user_data(10)
        
        # Calculate basic statistics
        stats = calculate_statistics(users)
        
        # Process the statistics
        processed = process_statistics(stats)
        
        # Generate final report
        report = generate_report(processed)
        
        print("\nFinal Report:")
        print(report)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()