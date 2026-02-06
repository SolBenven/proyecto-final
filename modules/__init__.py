# Modules package

# Model classes — must be imported so SQLAlchemy registers them for
# string-based relationship() resolution across files.
from modules.user import User  # noqa: F401
from modules.end_user import EndUser, Cloister  # noqa: F401
from modules.admin_user import AdminUser, AdminRole  # noqa: F401
from modules.department import Department  # noqa: F401
from modules.claim import Claim, ClaimStatus  # noqa: F401
from modules.claim_supporter import ClaimSupporter  # noqa: F401
from modules.claim_status_history import ClaimStatusHistory  # noqa: F401
from modules.claim_transfer import ClaimTransfer  # noqa: F401
from modules.user_notification import UserNotification  # noqa: F401

# Infrastructure modules
from modules.classifier import classifier, Classifier
from modules.similarity import similarity_finder, SimilarityFinder
from modules.image_handler import ImageHandler

# Generator modules
from modules.analytics_generator import AnalyticsGenerator
from modules.report_generator import create_report, Report, HTMLReport, PDFReport

# Helper modules
from modules.admin_helper import AdminHelper
