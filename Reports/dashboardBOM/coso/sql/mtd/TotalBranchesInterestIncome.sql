/*MTD - BOM - CoSo*/

/*Total branches - Interest Income*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

WITH

[Branch] AS (
    SELECT DISTINCT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
)

, [BadDebt] AS (
	SELECT 
		CONVERT(VARCHAR(7), [Ngay], 126) [Ngay]
		, [SoTaiKhoan]
	FROM [BadDebtAccounts]
	WHERE [Ngay] BETWEEN DATEADD(MONTH, -1, @FirstDateOfMonth) AND @Date
		AND [LoaiNo] NOT IN (N'Hết nợ', N'TK đã đóng')
)

, [TargetByBranch] AS (
    SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'Interest Income'
        AND [Year] = YEAR(@Date)
)

, [ValueTotalBranches] AS (
	SELECT 
		[relationship].[branch_id] [BranchID]
		, SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [rln0019].[date] = [relationship].[date]
		AND [rln0019].[sub_account] = [relationship].[sub_account]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
	WHERE [rln0019].[date] BETWEEN @FirstDateOfMonth AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
	GROUP BY [relationship].[branch_id]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [InterestIncome]
		, CASE [InterestIncome] 
			WHEN 0 THEN 0
			ELSE [InterestIncome] / (SELECT SUM([InterestIncome]) FROM [ValueTotalBranches])
		END [Contribution]
	FROM [ValueTotalBranches]
)

SELECT
	RANK() OVER(ORDER BY ISNULL([InterestIncome], 0) DESC) [Rank]
	, [Branch].[BranchID]
	, ISNULL([InterestIncome], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]
ORDER BY 1


END