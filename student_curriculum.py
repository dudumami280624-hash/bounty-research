"""Machine-readable offline curriculum: teaching before blind evaluation."""
import json
from pathlib import Path

CURRICULUM = [
 {"id":"reentrancy-01","prerequisites":[],"topic":"重入漏洞","objectives":["理解外部调用与状态更新顺序","解释 CEI 与重入保护"],"reading":["https://docs.soliditylang.org/en/latest/security-considerations.html#reentrancy","https://docs.openzeppelin.com/contracts/5.x/api/utils#ReentrancyGuard"],"lab":"student_lab/test/ReentrancyLesson.t.sol","test_contract":"ReentrancyLessonTest","assessment":"reentrancy-01"},
 {"id":"access-control-01","prerequisites":["reentrancy-01"],"topic":"访问控制","objectives":["识别未授权敏感操作","解释角色与权限检查"],"reading":["https://docs.openzeppelin.com/contracts/5.x/access-control"],"lab":"student_lab/test/AccessControlLesson.t.sol","test_contract":"AccessControlLessonTest","assessment":"access-control-01"},
 {"id":"arithmetic-01","prerequisites":["access-control-01"],"topic":"整数精度","objectives":["识别舍入误差","设计边界和不变量测试"],"reading":["https://docs.soliditylang.org/en/latest/types.html#division_"],"lab":"student_lab/test/ArithmeticLesson.t.sol","test_contract":"ArithmeticLessonTest","assessment":"arithmetic-01"}
]
def curriculum():
    return {"version":1,"courses":CURRICULUM,"policy":"Prerequisites unlock only with verified assessment and real lab evidence; absent fixtures remain locked."}
if __name__=="__main__":
    print(json.dumps(curriculum(),ensure_ascii=False,indent=2))
